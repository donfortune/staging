import os

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.crud.base import get_db, get_company
from api.models import models
from api.models.models import Ranking

load_dotenv()
router = APIRouter()


@router.get('/company/ranking', tags=["Company"], )
def get_list_of_ranked_companies():
    db: Session = next(get_db())
    # get companies
    low_cap_category_id = os.getenv('LOW_MARKET_CAP_CATEGORY_ID')
    companies: list = db.query(models.Company).filter(models.Company.category != low_cap_category_id).all()

    # get latest rankings
    rankings: list = []
    for company in companies:
        rank = db.query(Ranking).filter(Ranking.company == company.company_id) \
            .order_by(Ranking.created_at.desc()).first()
        if rank:
            rankings.append(rank)

    # sort rankings by score (descending)
    def get_ranking_sort_key(inner_rank: Ranking):
        return inner_rank.score

    rankings.sort(key=get_ranking_sort_key, reverse=True)

    # create the response list
    response = []
    top_rankings = []
    for ranking in rankings:
        if len(top_rankings) == 12:
            break

        top_rankings.append(ranking)

    for ranking in top_rankings:
        comp: models.Company = ranking.comp_ranks
        data = {
            'company_id': comp.company_id,
            'name': comp.name,
            'market_cap': comp.market_cap,
            'sector': comp.sect_value,
            'category': comp.cat_value,
            'ticker_symbol': comp.ticker_value.symbol,
            'exchange_platform': comp.ticker_value.exchange_name,
            'current_ranking': {
                'score': ranking.score,
                'created_at': ranking.created_at
            }
        }
        response.append(data)

    return response


@router.get('/company/ranks/{category}', tags=["Company"], )
async def get_company_category(category: str):
    db: Session = next(get_db())
    # get companies
    companies: list = db.query(models.Company).filter(models.Company.category == category).all()

    # get latest rankings
    rankings: list = []
    for company in companies:
        rank = db.query(Ranking).filter(Ranking.company == company.company_id) \
            .order_by(Ranking.created_at.desc()).first()
        if rank:
            rankings.append(rank)

    # sort rankings by score (descending)
    def get_ranking_sort_key(inner_rank: Ranking):
        return inner_rank.score

    rankings.sort(key=get_ranking_sort_key, reverse=True)

    # create the response list
    response = []
    top_rankings = []
    for ranking in rankings:
        if len(top_rankings) == 12:
            break

        top_rankings.append(ranking)

    for ranking in top_rankings:
        comp: models.Company = ranking.comp_ranks
        data = {
            'company_id': comp.company_id,
            'name': comp.name,
            'sector': comp.sect_value,
            'category': comp.cat_value,
            'ticker_symbol': comp.ticker_value.symbol,
            'exchange_platform': comp.ticker_value.exchange_name,
            'current_ranking': {
                'score': ranking.score,
                'created_at': ranking.created_at
            }
        }
        response.append(data)

    return response


@router.get('/company/{company_id}/interval', tags=["Company"], )
async def get_company_metrics_for_interval(company_id: str, startDate: str, endDate: str,
                                           db: Session = Depends(get_db)):
    """
    This gets the metrics of a company within a specified interval
    """
    company: models.Company = get_company(db, company_id=company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company info not available")

    stock_prices = db.query(models.StockPrice).filter(models.StockPrice.company == company_id,
                                                      models.StockPrice.date >= startDate,
                                                      models.StockPrice.date <= endDate
                                                      ).order_by(models.StockPrice.date.asc()).all()
    financials = db.query(models.Financial).filter(models.Financial.company == company_id,
                                                   models.Financial.date >= startDate,
                                                   models.Financial.date <= endDate
                                                   ).order_by(models.Financial.date.asc()).all()

    ranking = db.query(models.Ranking).filter(models.Ranking.company == company_id).order_by(
        models.Ranking.created_at.desc()).first()
    response = {
        'company_id': company.company_id,
        'name': company.name,
        'description': company.description,
        'sector': company.sect_value,
        'category': company.cat_value,
        'ticker': company.ticker_value,
        'current_ranking': ranking,
        'financials': financials,
        'stock_prices': stock_prices,
    }
    return response


@router.get('/company/{company_id}', tags=["Company"])
async def get_company_metrics(company_id: str, db: Session = Depends(get_db)):
    company: models.Company = get_company(db, company_id=company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company info not available")

    ranking = db.query(models.Ranking).filter(models.Ranking.company == company_id).order_by(
        models.Ranking.created_at.desc()).first()
    stock_price = db.query(models.StockPrice).filter(models.StockPrice.company == company_id).order_by(
        models.StockPrice.date.asc()).first()
    financials = db.query(models.Financial).filter(models.Financial.company == company_id).order_by(
        models.Financial.date.asc()).first()

    response = {
        'company_id': company.company_id,
        'name': company.name,
        'description': company.description,
        'sector': company.sect_value,
        'category': company.cat_value,
        'ticker': company.ticker_value,
        'current_ranking': ranking,
        'financials': financials,
        'stock_price': stock_price,
    }
    return response


@router.get('/company/{company_id}/ranking/history', tags=["Company"])
async def get_company_metrics(company_id: str, db: Session = Depends(get_db)):
    company: models.Company = get_company(db, company_id=company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company info not available")

    rankings = db.query(models.Ranking).filter(models.Ranking.company == company_id).order_by(
        models.Ranking.created_at.desc()).all()

    return rankings
