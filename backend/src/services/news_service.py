# src/services/news_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.news import MovieNewsTable, PromotionTable, UnifiedNewsCreate, UnifiedNewsResponse
from typing import List, Optional

class NewsService:
    @staticmethod
    async def get_all_unified(db: AsyncSession) -> List[UnifiedNewsResponse]:
        # Fetch MovieNews
        movie_news_stmt = select(MovieNewsTable).order_by(MovieNewsTable.published_at.desc())
        movie_news_res = await db.execute(movie_news_stmt)
        movie_news = movie_news_res.scalars().all()

        # Fetch Promotions
        promo_stmt = select(PromotionTable).order_by(PromotionTable.created_at.desc())
        promo_res = await db.execute(promo_stmt)
        promotions = promo_res.scalars().all()

        unified_list = []
        for mn in movie_news:
            unified_list.append(UnifiedNewsResponse(
                id=mn.news_id,
                title=mn.title,
                content=mn.content,
                type="Tin Phim",
                status="Published", # Giả định MovieNews luôn published
                publishDate=mn.published_at.strftime("%Y-%m-%d") if mn.published_at else None,
                thumbnail=mn.image_url,
                movieId=mn.movie_id
            ))

        for pr in promotions:
            unified_list.append(UnifiedNewsResponse(
                id=pr.promo_id,
                title=pr.title,
                content=pr.content,
                type=pr.type,
                status=pr.status,
                publishDate=pr.start_date.strftime("%Y-%m-%d") if pr.start_date else (pr.created_at.strftime("%Y-%m-%d") if pr.created_at else None),
                thumbnail=pr.banner_url,
                movieId=None
            ))

        # Sort by date descending
        unified_list.sort(key=lambda x: x.publishDate or "", reverse=True)
        return unified_list

    @staticmethod
    async def create_unified(db: AsyncSession, data: UnifiedNewsCreate) -> UnifiedNewsResponse:
        if data.type == "Tin Phim":
            new_mn = MovieNewsTable(
                title=data.title,
                content=data.content,
                image_url=data.thumbnail,
                movie_id=data.movieId
            )
            db.add(new_mn)
            await db.flush()
            return UnifiedNewsResponse(
                id=new_mn.news_id, title=new_mn.title, content=new_mn.content,
                type="Tin Phim", status="Published", thumbnail=new_mn.image_url, movieId=new_mn.movie_id
            )
        else:
            new_pr = PromotionTable(
                title=data.title,
                content=data.content,
                type=data.type,
                status=data.status,
                banner_url=data.thumbnail
            )
            db.add(new_pr)
            await db.flush()

            # Nếu tạo mới và Publish luôn thì phát thông báo
            if data.status == "Published":
                from src.models.user import UserTable
                from src.models.news import UserNotificationTable
                users_res = await db.execute(select(UserTable))
                all_users = users_res.scalars().all()
                for u in all_users:
                    db.add(UserNotificationTable(user_id=u.user_id, promo_id=new_pr.promo_id))
                await db.flush()

            return UnifiedNewsResponse(
                id=new_pr.promo_id, title=new_pr.title, content=new_pr.content,
                type=new_pr.type, status=new_pr.status, thumbnail=new_pr.banner_url, movieId=None
            )

    @staticmethod
    async def update_unified(db: AsyncSession, news_id: int, data: UnifiedNewsCreate) -> Optional[UnifiedNewsResponse]:
        if data.type == "Tin Phim":
            res = await db.execute(select(MovieNewsTable).where(MovieNewsTable.news_id == news_id))
            mn = res.scalar_one_or_none()
            if not mn: return None
            mn.title = data.title
            mn.content = data.content
            mn.image_url = data.thumbnail
            mn.movie_id = data.movieId
            await db.flush()
            return UnifiedNewsResponse(
                id=mn.news_id, title=mn.title, content=mn.content,
                type="Tin Phim", status="Published", thumbnail=mn.image_url, movieId=mn.movie_id
            )
        else:
            res = await db.execute(select(PromotionTable).where(PromotionTable.promo_id == news_id))
            pr = res.scalar_one_or_none()
            if not pr: return None
            
            was_draft = pr.status != "Published"
            
            pr.title = data.title
            pr.content = data.content
            pr.type = data.type
            pr.status = data.status
            pr.banner_url = data.thumbnail
            await db.flush()

            # Nếu chuyển từ Draft -> Published thì phát thông báo
            if was_draft and data.status == "Published":
                from src.models.user import UserTable
                from src.models.news import UserNotificationTable
                users_res = await db.execute(select(UserTable))
                all_users = users_res.scalars().all()
                for u in all_users:
                    db.add(UserNotificationTable(user_id=u.user_id, promo_id=pr.promo_id))
                await db.flush()

            return UnifiedNewsResponse(
                id=pr.promo_id, title=pr.title, content=pr.content,
                type=pr.type, status=pr.status, thumbnail=pr.banner_url, movieId=None
            )

    @staticmethod
    async def delete_unified(db: AsyncSession, news_id: int, item_type: str) -> bool:
        if item_type == "Tin Phim":
            res = await db.execute(select(MovieNewsTable).where(MovieNewsTable.news_id == news_id))
            mn = res.scalar_one_or_none()
            if not mn: return False
            await db.delete(mn)
        else:
            res = await db.execute(select(PromotionTable).where(PromotionTable.promo_id == news_id))
            pr = res.scalar_one_or_none()
            if not pr: return False
            await db.delete(pr)
        await db.flush()
        return True