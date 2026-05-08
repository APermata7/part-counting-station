from app.schemas.inspection import StatusEnum

def determine_status(difference: int, threshold: int) -> StatusEnum:
    """
    OK if difference <= threshold, else NG.
    """
    return StatusEnum.OK if difference <= threshold else StatusEnum.NG