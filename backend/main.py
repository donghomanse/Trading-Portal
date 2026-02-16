from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from contextlib import asynccontextmanager

from database import get_db, init_db
from models import Trade
from schemas import TradeCreate, TradeResponse, TradeUpdate

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    await init_db()
    yield
    # Shutdown: cleanup if needed

app = FastAPI(title="Trading Portal API", lifespan=lifespan)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
@app.get("/api")
async def root():
    return {"message": "Welcome to Trading Portal API"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

# Trade CRUD endpoints
@app.post("/api/trades", response_model=TradeResponse, status_code=201)
async def create_trade(trade: TradeCreate, db: AsyncSession = Depends(get_db)):
    """Create a new trade"""
    db_trade = Trade(**trade.model_dump())
    db.add(db_trade)
    await db.commit()
    await db.refresh(db_trade)
    return db_trade

@app.get("/api/trades", response_model=List[TradeResponse])
async def get_trades(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Get all trades"""
    result = await db.execute(select(Trade).offset(skip).limit(limit))
    trades = result.scalars().all()
    return trades

@app.get("/api/trades/{trade_id}", response_model=TradeResponse)
async def get_trade(trade_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific trade by ID"""
    result = await db.execute(select(Trade).where(Trade.id == trade_id))
    trade = result.scalar_one_or_none()
    if trade is None:
        raise HTTPException(status_code=404, detail="Trade not found")
    return trade

@app.patch("/api/trades/{trade_id}", response_model=TradeResponse)
async def update_trade(trade_id: int, trade_update: TradeUpdate, db: AsyncSession = Depends(get_db)):
    """Update a trade"""
    result = await db.execute(select(Trade).where(Trade.id == trade_id))
    trade = result.scalar_one_or_none()
    if trade is None:
        raise HTTPException(status_code=404, detail="Trade not found")

    update_data = trade_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(trade, key, value)

    await db.commit()
    await db.refresh(trade)
    return trade

@app.delete("/api/trades/{trade_id}", status_code=204)
async def delete_trade(trade_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a trade"""
    result = await db.execute(select(Trade).where(Trade.id == trade_id))
    trade = result.scalar_one_or_none()
    if trade is None:
        raise HTTPException(status_code=404, detail="Trade not found")

    await db.delete(trade)
    await db.commit()
    return None

# Serve static files from frontend/dist
static_dir = Path(__file__).parent.parent / "frontend" / "dist"
if static_dir.exists():
    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve the React SPA for all non-API routes"""
        file_path = static_dir / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        # Return index.html for SPA routing
        return FileResponse(static_dir / "index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
