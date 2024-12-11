import os
import asyncio
import asyncpg
import aiohttp
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")

headers = {}
if GITHUB_TOKEN:
    headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

SEARCH_URL = "https://api.github.com/search/repositories?q=stars:%3E1&sort=stars&order=desc&per_page=100"
COMMITS_URL_TEMPLATE = "https://api.github.com/repos/{owner}/{repo}/commits"

async def fetch_json(session, url, **kwargs):
    async with session.get(url, headers=headers, **kwargs) as resp:
        resp.raise_for_status()
        return await resp.json()

async def main():
    pool = await asyncpg.create_pool(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        database=POSTGRES_DB,
        min_size=1,
        max_size=5
    )

    async with aiohttp.ClientSession() as session:
        data = await fetch_json(session, SEARCH_URL)
        items = data.get("items", [])

        async with pool.acquire() as conn:
            await conn.execute("TRUNCATE TABLE top100;")
            position = 1
            insert_query = """
            INSERT INTO top100 (repo, owner, position_cur, position_prev, stars, watchers, forks, open_issues, language)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
            """
            for item in items:
                await conn.execute(insert_query,
                                   item["name"],
                                   item["owner"]["login"],
                                   position,
                                   None,
                                   item["stargazers_count"],
                                   item["watchers_count"],
                                   item["forks_count"],
                                   item["open_issues_count"],
                                   item["language"])
                position += 1

        since = (datetime.utcnow() - timedelta(days=7)).isoformat() + "Z"
        until = datetime.utcnow().isoformat() + "Z"

        async with pool.acquire() as conn:
            await conn.execute("DELETE FROM activity WHERE date >= $1 AND date <= $2", since[:10], until[:10])

            for item in items:
                owner = item["owner"]["login"]
                repo = item["name"]
                commits_url = COMMITS_URL_TEMPLATE.format(owner=owner, repo=repo)
                commits_data = await fetch_json(session, commits_url, params={"since": since, "until": until, "per_page": 100})

                commits_by_date = {}
                for commit in commits_data:
                    commit_date = commit["commit"]["author"]["date"][:10]
                    author = commit["commit"]["author"]["name"]
                    if commit_date not in commits_by_date:
                        commits_by_date[commit_date] = {"count": 0, "authors": set()}
                    commits_by_date[commit_date]["count"] += 1
                    commits_by_date[commit_date]["authors"].add(author)

                insert_act_query = """
                INSERT INTO activity (owner, repo, date, commits, authors)
                VALUES ($1,$2,$3,$4,$5)
                ON CONFLICT (owner, repo, date)
                DO UPDATE SET commits = EXCLUDED.commits, authors = EXCLUDED.authors;
                """
                for d, info in commits_by_date.items():
                    await conn.execute(insert_act_query, owner, repo, d, info["count"], list(info["authors"]))

    await pool.close()

def handler(event, context):
    asyncio.run(main())
    return {"status": "ok"}
