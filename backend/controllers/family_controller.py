import os
from dotenv import load_dotenv
from fastapi import status
from datetime import datetime, time, timezone
from sqlalchemy.orm import joinedload
from sqlalchemy import and_, or_
from sqlalchemy.exc import SQLAlchemyError
from models.models import Family, Task
from schemas.schemas import TaskResponse
from structlog import get_logger
from utils.error_handler import AppError, ErrorCode

load_dotenv()

logger = get_logger()


def get_family_by_id(db, family_id: str) -> Family:
    """
    Retrieve family by ID with users preloaded.
    
    Args:
        db: Database session
        family_id: Public ID of the family
        
    Returns:
        Family: Family object with users loaded
        
    Raises:
        AppError: If family not found
    """
    family = (
        db.query(Family)
        .options(joinedload(Family.users))
        .filter(Family.public_id == family_id)
        .first()
    )

    if not family:
        raise AppError(
            code=ErrorCode.NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
            technical_message=f"Family not found with ID: {family_id}",
            user_message="The family you're looking for could not be found",
            is_operational=True,
            details={"family_id": family_id}
        )

    return family


def parse_date_to_utc_range(date_str: str) -> tuple[datetime, datetime]:
    """
    Parse ISO date string to UTC datetime range (start and end of day).
    
    Args:
        date_str: ISO format date string
        
    Returns:
        tuple: (start_of_day, end_of_day) in UTC
        
    Raises:
        AppError: If date parsing fails
    """
    try:
        parsed_date = datetime.fromisoformat(date_str).date()
        start_of_day = datetime.combine(parsed_date, time.min).replace(
            tzinfo=timezone.utc
        )
        end_of_day = datetime.combine(parsed_date, time.max).replace(
            tzinfo=timezone.utc
        )
        return start_of_day, end_of_day
    except (ValueError, TypeError) as e:
        raise AppError(
            code=ErrorCode.VALIDATION_ERROR,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            technical_message=f"Date parsing failed for '{date_str}': {str(e)}",
            user_message="Invalid date format. Please provide a valid date",
            is_operational=True,
            details={"date_provided": date_str, "expected_format": "ISO 8601"}
        )


def query_tasks_for_date(
    db, family_id: str, start_of_day: datetime, end_of_day: datetime
) -> list[Task]:
    """
    Query tasks for a family within a specific date range.
    
    Logic:
    - Include tasks created on the specified date
    - Include tasks due on/after the date that are not completed
    - Exclude soft-deleted tasks
    
    Args:
        db: Database session
        family_id: Family public ID
        start_of_day: Start of date range (UTC)
        end_of_day: End of date range (UTC)
        
    Returns:
        list[Task]: Ordered list of tasks (by due_date ascending)
        
    Raises:
        AppError: If database query fails
    """
    try:
        return (
            db.query(Task)
            .filter(
                and_(
                    Task.family_id == family_id,
                    Task.is_deleted == False,
                    or_(
                        and_(
                            Task.created_at >= start_of_day,
                            Task.created_at <= end_of_day,
                        ),
                        and_(
                            Task.due_date >= start_of_day,
                            Task.status != "completed"
                        ),
                    ),
                )
            )
            .order_by(Task.due_date.asc())
            .all()
        )
    except SQLAlchemyError as e:
        raise AppError(
            code=ErrorCode.INTERNAL_SERVER_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            technical_message=f"Database query failed for family tasks: {str(e)}",
            user_message="Unable to retrieve tasks at this time",
            is_operational=True,
            details={
                "family_id": family_id,
                "date_range": {
                    "start": start_of_day.isoformat(),
                    "end": end_of_day.isoformat()
                }
            }
        )


async def get_family(id: str, db) -> Family:
    """
    Get family by ID with full error handling.
    
    Args:
        id: Family public ID
        db: Database session
        
    Returns:
        Family: Family object with users
        
    Raises:
        AppError: For any errors during retrieval
    """
    logger.info("get_family_started", family_id=id)

    try:
        family = get_family_by_id(db, id)
        logger.info("get_family_completed", family_id=id)
        return family

    except AppError:
        # Re-raise AppErrors with context already set
        raise

    except SQLAlchemyError as e:
        raise AppError(
            code=ErrorCode.INTERNAL_SERVER_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            technical_message=f"Database error retrieving family: {str(e)}",
            user_message="Unable to retrieve family information",
            is_operational=True,
            details={"family_id": id}
        )

    except Exception as e:
        # Catch-all for unexpected errors
        raise AppError(
            code=ErrorCode.INTERNAL_SERVER_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            technical_message=f"Unexpected error in get_family: {type(e).__name__}: {str(e)}",
            user_message="An unexpected error occurred",
            is_operational=False,
            details={"family_id": id, "error_type": type(e).__name__}
        )


async def get_family_task_for_date(
    family_id: str, date: str, db
) -> list[TaskResponse]:
    """
    Get all tasks for a family on a specific date.
    
    Includes:
    - Tasks created on that date
    - Tasks due on/after that date (if not completed)
    
    Args:
        family_id: Family public ID
        date: ISO format date string
        db: Database session
        
    Returns:
        list[TaskResponse]: List of tasks (empty list if none found)
        
    Raises:
        AppError: For validation or database errors
    """
    logger.info("get_family_task_for_date_started", family_id=family_id, date=date)

    try:
        # Validate family exists first
        get_family_by_id(db, family_id)
        
        # Parse date and get range
        start_of_day, end_of_day = parse_date_to_utc_range(date)
        
        logger.info(
            "date_range_parsed",
            start_of_day=start_of_day.isoformat(),
            end_of_day=end_of_day.isoformat(),
        )

        # Query tasks
        tasks = query_tasks_for_date(db, family_id, start_of_day, end_of_day)

        if not tasks:
            logger.info("no_tasks_found", family_id=family_id, date=date)
            return []

        logger.info(
            "get_family_task_for_date_completed",
            family_id=family_id,
            task_count=len(tasks),
        )
        
        return [TaskResponse.model_validate(task) for task in tasks]

    except AppError:
        # Re-raise AppErrors (from get_family_by_id, parse_date, or query_tasks)
        raise

    except ValueError as e:
        # Pydantic validation errors when creating TaskResponse
        raise AppError(
            code=ErrorCode.VALIDATION_ERROR,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            technical_message=f"Task validation failed: {str(e)}",
            user_message="Error processing task data",
            is_operational=True,
            details={"family_id": family_id, "date": date}
        )

    except SQLAlchemyError as e:
        raise AppError(
            code=ErrorCode.INTERNAL_SERVER_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            technical_message=f"Database error in get_family_task_for_date: {str(e)}",
            user_message="Unable to retrieve tasks",
            is_operational=True,
            details={"family_id": family_id, "date": date}
        )

    except Exception as e:
        # Unexpected errors
        raise AppError(
            code=ErrorCode.INTERNAL_SERVER_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            technical_message=f"Unexpected error in get_family_task_for_date: {type(e).__name__}: {str(e)}",
            user_message="An unexpected error occurred while retrieving tasks",
            is_operational=False,
            details={
                "family_id": family_id,
                "date": date,
                "error_type": type(e).__name__
            }
        )