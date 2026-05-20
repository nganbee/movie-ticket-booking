from fastapi import Header, HTTPException, status

def verify_admin(admin_key: str = Header(..., description="Mã khóa xác thực Admin")):
    if admin_key != "secret_admin_123":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền thực hiện chức năng này"
        )
