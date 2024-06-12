import json

import bcrypt
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import Column, Integer, String, create_engine, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

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


# 定义设备模型
class Device(Base):
    __tablename__ = 'devices'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    type = Column(String(50))
    status = Column(Boolean, default=False)  # 0 for off, 1 for on


Base.metadata.create_all(bind=engine)

# FastAPI 应用
app = FastAPI()

# 挂载静态文件到 /static 路径
app.mount("/static", StaticFiles(directory="static"), name="static")

# 设置自定义模板目录
templates = Jinja2Templates(directory="web")


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


@app.get("/devices", response_class=HTMLResponse)
async def read_devices(request: Request):
    return templates.TemplateResponse("devices.html", {"request": request})


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
    return {"success": True, "redirect_url": "/devices"}


# 查询设备信息接口
@app.get("/api/devices")
async def get_devices(db: Session = Depends(get_db)):
    devices = db.query(Device).all()
    return devices


# WebSocket 端点
@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if message['action'] == 'connect':
                device_id = message.get('device_id')
                device = db.query(Device).filter(Device.id == device_id).first()
                if device:
                    device.status = True
                    db.commit()
                    await websocket.send_text(f"设备 {device.name} 已连接")
            elif message['action'] == 'toggle':
                device_id = message.get('device_id')
                device = db.query(Device).filter(Device.id == device_id).first()
                if device:
                    device.status = not device.status
                    db.commit()
                    await websocket.send_text(f"【{device.name}】现在是【{'开启' if device.status else '关闭'}】状态 ")
    except WebSocketDisconnect as e:
        print(f"WebSocket 连接断开: {e}")
    except Exception as e:
        print(f"错误: {e}")


# 运行应用
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8602, reload=True)
