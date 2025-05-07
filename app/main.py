from fastapi import FastAPI
from app.routes import challenge, refine, journal
#, report, journal

app = FastAPI()

app.include_router(challenge.router, prefix="/challenge")
app.include_router(refine.router, prefix="/refine")
#app.include_router(report.router, prefix="/report")
app.include_router(journal.router, prefix="/journal")
