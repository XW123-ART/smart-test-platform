from app.routes import app 

if __name__ == '__main__': 
    print("🚀 启动智能测试平台...") 
    print("访问地址：http://127.0.0.1:5000") 
    app.run(debug=True, host='0.0.0.0', port=5000)