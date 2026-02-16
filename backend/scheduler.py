"""스케줄러 설정 - KOSPI 마스터 데이터 자동 업데이트"""

import os
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

from download_kospi_master import kospi_master_download, get_kospi_master_dataframe, save_to_database

# 스케줄러 인스턴스
scheduler = AsyncIOScheduler()

async def update_kospi_master():
    """KOSPI 마스터 데이터 다운로드 및 DB 업데이트"""
    try:
        print(f"\n[SCHEDULER] Starting KOSPI master update at {datetime.now()}")

        base_dir = os.getcwd()

        # 1. 마스터 파일 다운로드
        print("[SCHEDULER] Downloading KOSPI master file...")
        kospi_master_download(base_dir, verbose=False)

        # 2. 데이터프레임으로 변환
        print("[SCHEDULER] Processing KOSPI master data...")
        df = get_kospi_master_dataframe(base_dir)

        # 3. 데이터베이스에 저장
        print("[SCHEDULER] Saving to database...")
        await save_to_database(df)

        # 4. Excel 파일로도 저장 (백업)
        print("[SCHEDULER] Saving to Excel...")
        df.to_excel('kospi_code.xlsx', index=False)

        # 5. JSON 파일로도 저장 (백업)
        print("[SCHEDULER] Saving to JSON...")
        df.to_json('kospi_code.json', orient='records', force_ascii=False, indent=2)

        print(f"[SCHEDULER] KOSPI master update completed successfully!")
        print(f"[SCHEDULER] Total stocks: {len(df)}")
        print(f"[SCHEDULER] Next update: Tomorrow at 22:00")

    except Exception as e:
        print(f"[SCHEDULER ERROR] Failed to update KOSPI master: {str(e)}")
        import traceback
        traceback.print_exc()


def start_scheduler():
    """스케줄러 시작 - 매일 밤 10시에 KOSPI 마스터 업데이트"""
    # 매일 밤 10시(22:00)에 실행
    scheduler.add_job(
        update_kospi_master,
        trigger=CronTrigger(hour=22, minute=0),
        id='kospi_master_update',
        name='Daily KOSPI Master Update',
        replace_existing=True
    )

    scheduler.start()
    print("[SCHEDULER] Started - KOSPI master data will be updated daily at 22:00")

    # 다음 실행 시간 출력
    next_run = scheduler.get_job('kospi_master_update').next_run_time
    print(f"[SCHEDULER] Next run time: {next_run}")


def stop_scheduler():
    """스케줄러 종료"""
    if scheduler.running:
        scheduler.shutdown()
        print("[SCHEDULER] Stopped")


async def run_now():
    """즉시 실행 (테스트용)"""
    print("[SCHEDULER] Running KOSPI master update immediately...")
    await update_kospi_master()
