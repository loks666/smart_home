from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import uvicorn
import bcrypt

# 配置数据库
DATABASE_URL = "mysql+pymysql://root:Lx284190056!@localhost/smart"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 定义用户模型
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, comment="用户ID")
    username = Column(String(255), unique=True, index=True, comment="用户名")
    hashed_password = Column(String(255), comment="哈希加密后的密码")

Base.metadata.create_all(bind=engine)

# FastAPI 应用
app = FastAPI()

# 挂载静态文件到 /static 路径
app.mount("/static", StaticFiles(directory="static"), name="static")

# 设置自定义模板目录
templates = Jinja2Templates(directory="web")

# 定义Pydantic模型
class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 路由和视图函数
@app.get("/", response_class=HTMLResponse)
@app.get("/login", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def read_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# 注册接口
@app.post("/api/register")
async def register(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    print(f"Received register data: username={username}, password={password}")  # 添加调试信息，打印接收到的数据
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    db_user = User(username=username, hashed_password=hashed_password.decode('utf-8'))
    db.add(db_user)
    db.commit()
    return {"success": True}

# 登录接口
@app.post("/api/login")
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    print(f"Received login data: username={username}, password={password}")  # 添加调试信息，打印接收到的数据
    db_user = db.query(User).filter(User.username == username).first()
    if db_user is None or not bcrypt.checkpw(password.encode('utf-8'), db_user.hashed_password.encode('utf-8')):
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    return {"success": True}

# 运行应用
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8602, reload=True)
