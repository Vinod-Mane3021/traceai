import asyncio
import random
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session_maker, engine
from app.models.core import Repository, PullRequest, Vulnerability
from sqlalchemy import select, delete

async def seed_data():
    async with async_session_maker() as session:
        async with session.begin():
            # Optional: Clear existing data if you want a fresh start
            # await session.execute(delete(Vulnerability))
            # await session.execute(delete(PullRequest))
            # await session.execute(delete(Repository))

            print("Seeding repositories...")
            repos = [
                Repository(github_id=101, name="webapp-frontend", full_name="org/webapp-frontend"),
                Repository(github_id=102, name="auth-service", full_name="org/auth-service"),
                Repository(github_id=103, name="payment-gateway", full_name="org/payment-gateway"),
            ]
            session.add_all(repos)
            await session.flush() # To get IDs

            print("Seeding pull requests...")
            prs = []
            for repo in repos:
                for i in range(1, 4): # 3 PRs per repo
                    pr = PullRequest(
                        github_pr_id=random.randint(1000, 9999),
                        number=i,
                        state="open" if i < 3 else "closed",
                        title=f"Fix issue #{random.randint(1, 100)} in {repo.name}",
                        repository_id=repo.id
                    )
                    prs.append(pr)
            session.add_all(prs)
            await session.flush()

            print("Seeding vulnerabilities...")
            severities = ["High", "Medium", "Low"]
            statuses = ["open", "resolved", "ignored"]
            file_paths = [
                "src/auth/login.py",
                "app/api/payments.py",
                "utils/helper.js",
                "config/settings.yaml",
                "src/database/connection.py"
            ]
            
            vulnerabilities = []
            for pr in prs:
                num_vulns = random.randint(0, 5) # Random number of vulns per PR
                for _ in range(num_vulns):
                    vuln = Vulnerability(
                        pull_request_id=pr.id,
                        file_path=random.choice(file_paths),
                        line_number=random.randint(1, 500),
                        severity=random.choice(severities),
                        description=f"Potential security risk detected in {random.choice(['input validation', 'SQL query', 'dependency version'])}.",
                        status=random.choice(statuses)
                    )
                    vulnerabilities.append(vuln)
            
            session.add_all(vulnerabilities)
            
        await session.commit()
        print(f"Successfully seeded {len(repos)} repos, {len(prs)} PRs, and {len(vulnerabilities)} vulnerabilities.")

if __name__ == "__main__":
    asyncio.run(seed_data())
