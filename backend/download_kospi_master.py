"""코스피주식종목코드(kospi_code.mst) 정제 파이썬 파일"""

import urllib.request
import ssl
import zipfile
import os
import pandas as pd
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from database import Base, DATABASE_URL
from models import Stock

base_dir = os.getcwd()

def kospi_master_download(base_dir, verbose=False):
    cwd = os.getcwd()
    if verbose:
        print(f"current directory is {cwd}")
    ssl._create_default_https_context = ssl._create_unverified_context

    urllib.request.urlretrieve("https://new.real.download.dws.co.kr/common/master/kospi_code.mst.zip",
                               base_dir + "\\kospi_code.zip")

    os.chdir(base_dir)
    if verbose:
        print(f"change directory to {base_dir}")
    kospi_zip = zipfile.ZipFile('kospi_code.zip')
    kospi_zip.extractall()

    kospi_zip.close()

    if os.path.exists("kospi_code.zip"):
        os.remove("kospi_code.zip")


def get_kospi_master_dataframe(base_dir):
    file_name = base_dir + "\\kospi_code.mst"
    tmp_fil1 = base_dir + "\\kospi_code_part1.tmp"
    tmp_fil2 = base_dir + "\\kospi_code_part2.tmp"

    wf1 = open(tmp_fil1, mode="w")
    wf2 = open(tmp_fil2, mode="w")

    with open(file_name, mode="r", encoding="cp949") as f:
        for row in f:
            rf1 = row[0:len(row) - 228]
            rf1_1 = rf1[0:9].rstrip()
            rf1_2 = rf1[9:21].rstrip()
            rf1_3 = rf1[21:].strip()
            wf1.write(rf1_1 + ',' + rf1_2 + ',' + rf1_3 + '\n')
            rf2 = row[-228:]
            wf2.write(rf2)

    wf1.close()
    wf2.close()

    part1_columns = ['단축코드', '표준코드', '한글명']
    df1 = pd.read_csv(tmp_fil1, header=None, names=part1_columns, encoding='cp949')

    field_specs = [2, 1, 4, 4, 4,
                   1, 1, 1, 1, 1,
                   1, 1, 1, 1, 1,
                   1, 1, 1, 1, 1,
                   1, 1, 1, 1, 1,
                   1, 1, 1, 1, 1,
                   1, 9, 5, 5, 1,
                   1, 1, 2, 1, 1,
                   1, 2, 2, 2, 3,
                   1, 3, 12, 12, 8,
                   15, 21, 2, 7, 1,
                   1, 1, 1, 1, 9,
                   9, 9, 5, 9, 8,
                   9, 3, 1, 1, 1
                   ]

    part2_columns = ['그룹코드', '시가총액규모', '지수업종대분류', '지수업종중분류', '지수업종소분류',
                     '제조업', '저유동성', '지배구조지수종목', 'KOSPI200섹터업종', 'KOSPI100',
                     'KOSPI50', 'KRX', 'ETP', 'ELW발행', 'KRX100',
                     'KRX자동차', 'KRX반도체', 'KRX바이오', 'KRX은행', 'SPAC',
                     'KRX에너지화학', 'KRX철강', '단기과열', 'KRX미디어통신', 'KRX건설',
                     'Non1', 'KRX증권', 'KRX선박', 'KRX섹터_보험', 'KRX섹터_운송',
                     'SRI', '기준가', '매매수량단위', '시간외수량단위', '거래정지',
                     '정리매매', '관리종목', '시장경고', '경고예고', '불성실공시',
                     '우회상장', '락구분', '액면변경', '증자구분', '증거금비율',
                     '신용가능', '신용기간', '전일거래량', '액면가', '상장일자',
                     '상장주수', '자본금', '결산월', '공모가', '우선주',
                     '공매도과열', '이상급등', 'KRX300', 'KOSPI', '매출액',
                     '영업이익', '경상이익', '당기순이익', 'ROE', '기준년월',
                     '시가총액', '그룹사코드', '회사신용한도초과', '담보대출가능', '대주가능'
                     ]

    df2 = pd.read_fwf(tmp_fil2, widths=field_specs, names=part2_columns)

    df = pd.merge(df1, df2, how='outer', left_index=True, right_index=True)

    # clean temporary file and dataframe
    del df1
    del df2
    os.remove(tmp_fil1)
    os.remove(tmp_fil2)

    print("Done")

    return df


async def save_to_database(df):
    """DataFrame 데이터를 데이터베이스에 저장"""
    print("[DB] Connecting to database...")

    # 비동기 엔진 생성
    engine = create_async_engine(DATABASE_URL, echo=False)

    # 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 세션 생성
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # 기존 데이터 삭제
        print("[DB] Clearing existing stock data...")
        await session.execute(text("DELETE FROM stocks"))

        print("[DB] Inserting stock data...")
        inserted = 0

        for _, row in df.iterrows():
            stock = Stock(
                code=str(row['단축코드']).strip(),
                standard_code=str(row['표준코드']).strip() if pd.notna(row['표준코드']) else None,
                name=str(row['한글명']).strip(),
                market='KOSPI',
                group_code=str(row['그룹코드']).strip() if pd.notna(row['그룹코드']) else None,

                # 가격 정보
                base_price=int(row['기준가']) if pd.notna(row['기준가']) and row['기준가'] != '' else None,
                market_cap=float(row['시가총액']) if pd.notna(row['시가총액']) and row['시가총액'] != '' else None,

                # 상장 정보
                listing_date=str(row['상장일자']) if pd.notna(row['상장일자']) else None,
                listing_shares=float(row['상장주수']) if pd.notna(row['상장주수']) and row['상장주수'] != '' else None,
                capital=float(row['자본금']) if pd.notna(row['자본금']) and row['자본금'] != '' else None,
                par_value=float(row['액면가']) if pd.notna(row['액면가']) and row['액면가'] != '' else None,

                # 재무 정보
                revenue=float(row['매출액']) if pd.notna(row['매출액']) and row['매출액'] != '' else None,
                operating_profit=float(row['영업이익']) if pd.notna(row['영업이익']) and row['영업이익'] != '' else None,
                net_profit=float(row['당기순이익']) if pd.notna(row['당기순이익']) and row['당기순이익'] != '' else None,
                roe=float(row['ROE']) if pd.notna(row['ROE']) and row['ROE'] != '' else None,
                fiscal_month=str(row['결산월']) if pd.notna(row['결산월']) else None,

                # KRX 분류
                krx=str(row['KRX']) if pd.notna(row['KRX']) else None,
                krx_semiconductor=str(row['KRX반도체']) if pd.notna(row['KRX반도체']) else None,
                krx_bio=str(row['KRX바이오']) if pd.notna(row['KRX바이오']) else None,
                krx_banking=str(row['KRX은행']) if pd.notna(row['KRX은행']) else None,
                krx_auto=str(row['KRX자동차']) if pd.notna(row['KRX자동차']) else None,
                krx300=str(row['KRX300']) if pd.notna(row['KRX300']) else None,
                kospi=str(row['KOSPI']) if pd.notna(row['KOSPI']) else None,
                etp=str(row['ETP']) if pd.notna(row['ETP']) else None,

                # 거래 정보
                margin_rate=int(row['증거금비율']) if pd.notna(row['증거금비율']) and row['증거금비율'] != '' else None,
                credit_available=str(row['신용가능']) if pd.notna(row['신용가능']) else None,
                suspended=str(row['거래정지']) if pd.notna(row['거래정지']) else None,
                administered=str(row['관리종목']) if pd.notna(row['관리종목']) else None,
            )
            session.add(stock)
            inserted += 1

            # 100개마다 커밋
            if inserted % 100 == 0:
                await session.commit()
                print(f"[DB] Inserted {inserted} stocks...")

        # 최종 커밋
        await session.commit()
        print(f"[DB] Total {inserted} stocks inserted successfully!")

    await engine.dispose()


if __name__ == "__main__":
    print("[START] Downloading KOSPI master file...")
    kospi_master_download(base_dir, verbose=True)

    print("[PROCESSING] Processing KOSPI master data...")
    df = get_kospi_master_dataframe(base_dir)

    # 필요한 종목만 필터링 (예: KRX증권 제외)
    # df3 = df[df['KRX증권'] == 'Y']
    df3 = df

    # Excel 파일로 저장
    print("[SAVING] Saving to Excel...")
    df3.to_excel('kospi_code.xlsx', index=False)

    # JSON 파일로도 저장
    print("[SAVING] Saving to JSON...")
    df3.to_json('kospi_code.json', orient='records', force_ascii=False, indent=2)

    # 데이터베이스에 저장
    print("\n[DATABASE] Saving to database...")
    asyncio.run(save_to_database(df3))

    print(f"\n[SUCCESS] KOSPI master file downloaded!")
    print(f"[INFO] Total stocks: {len(df3)}")
    print(f"[INFO] Excel file: {os.path.abspath('kospi_code.xlsx')}")
    print(f"[INFO] JSON file: {os.path.abspath('kospi_code.json')}")
    print(f"[INFO] Database: stocks table updated")

    # 샘플 출력
    print("\n[SAMPLE] First 5 stocks:")
    print(df3[['단축코드', '한글명', 'KRX', '기준가', '상장일자', 'ROE']].head())
