import webview
import subprocess
import ctypes
import sys
import os

# ---------- 权限与系统检查 ----------
def is_admin():
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False

def run_as_admin():
    """以管理员身份重新启动程序"""
    if is_admin():
        return True
    else:
        try:
            # 获取当前脚本路径
            if hasattr(sys, 'frozen'):
                # 如果是打包后的exe
                script = sys.executable
            else:
                # 如果是Python脚本
                script = os.path.abspath(__file__)
            
            # 以管理员身份重新运行
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, f'"{script}"', None, 1
            )
            return False
        except Exception:
            return False

def check_auto_tz():
    # 检查 tzautoupdate 服务是否运行（自动设置时区）
    try:
        out = subprocess.check_output(["sc", "query", "tzautoupdate"], text=True, encoding="utf-8", errors="ignore")
        if "RUNNING" in out:
            return "RUNNING"
        elif "STOPPED" in out:
            return "STOPPED"
        else:
            return "UNKNOWN"
    except Exception:
        return "UNKNOWN"

# ---------- 后端 API ----------
class Api:
    def set_timezone(self, tzid: str):
        try:
            subprocess.run(["tzutil", "/s", tzid], check=True)
            return f"✅ 已切换到：{tzid}"
        except subprocess.CalledProcessError:
            return "❌ 修改失败：请确认已关闭\"自动设置时区\"。"
        except Exception as e:
            return f"❌ 异常：{e}"

    def check_admin(self):
        return is_admin()

    def check_auto_tz(self):
        return check_auto_tz()

# ---------- HTML 界面 ----------
HTML = r"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta http-equiv="X-UA-Compatible" content="IE=edge" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>时区切换器</title>
<style>
  :root{
    --red:#8B0000;
    --red-dark:#6e0000;
    --card:#ffffff;
    --bg:#f5f6f8;
    --text:#222;
    --muted:#666;
    --border:#e5e7eb;
  }
  *{box-sizing:border-box}
  html,body{height:100%}
  body{
    margin:0;
    background:var(--bg);
    color:var(--text);
    font-family: "Microsoft YaHei","Segoe UI",system-ui,-apple-system,Arial,sans-serif;
    -webkit-font-smoothing:antialiased;
    -moz-osx-font-smoothing:grayscale;
  }
  .container{
    max-width:640px;
    margin:24px auto;
    padding:0 16px;
  }
  h1{
    margin:0 0 12px;
    font-size:22px;
    font-weight:700;
  }
  .notice{
    display:none;
    margin:0 0 16px;
    padding:10px 12px;
    background:#fff7cc;
    border:1px solid #f1e6a6;
    color:#7a5d00;
    border-radius:10px;
  }
  .notice.show{display:block}
  .category{
    background:var(--card);
    border:1px solid var(--border);
    border-radius:14px;
    margin-bottom:14px;
    overflow:hidden;
    box-shadow:0 2px 8px rgba(0,0,0,.06);
  }
  .category-header{
    width:100%;
    text-align:left;
    padding:12px 16px;
    font-size:16px;
    font-weight:700;
    border:0;
    background:#ffffff;
    color:var(--text);
    cursor:pointer;
    display:flex;
    align-items:center;
    justify-content:space-between;
    transition:background .25s,color .25s;
  }
  .category-header .chev{
    transition:transform .35s ease;
    margin-left:12px;
    font-weight:900;
  }
  .category-header.active{
    background:var(--red);
    color:#fff;
  }
  .category-header.active .chev{
    transform:rotate(90deg);
  }
  .category-content{
    max-height:0;
    opacity:0;
    overflow:hidden;
    transition:max-height .4s ease, opacity .3s ease;
    background:#fff;
    border-top:1px solid var(--border);
  }
  .category-content-inner{
    padding:12px;
    display:flex;
    flex-direction:column;
    gap:10px;
  }
  .tzbtn{
    width:100%;
    text-align:left;
    padding:12px 14px;
    border:1px solid var(--red);
    background:var(--red);
    color:#fff;
    border-radius:10px;
    cursor:pointer;
    font-size:14px;
    display:flex;
    align-items:center;
    gap:10px;
    transition:background .2s,border-color .2s, transform .06s;
    min-height:48px;
  }
  .tzbtn:active{ transform:scale(0.995); }
  .tzbtn:hover{ background:var(--red-dark); border-color:var(--red-dark); }
  .flag{
    font-family: "Segoe UI Emoji","Apple Color Emoji","Noto Color Emoji","Twemoji Mozilla","Segoe UI Symbol",emoji,sans-serif;
    font-size:18px;
    line-height:1;
    display:inline-block;
    min-width:2ch;
    flex-shrink:0;
  }
  .label{
    white-space:normal;
    flex-grow:1;
  }
  .footer{
    margin-top:10px;
    font-size:12px;
    color:var(--muted);
  }
  .disabled{
    opacity:.6;
    pointer-events:none;
  }
</style>
</head>
<body>
  <div class="container">
    <h1>🌍 时区切换器 (管理员模式)</h1>
    <div id="autoTzWarn" class="notice">ℹ️ 检测到系统开启了"自动设置时区"（tzautoupdate）。为避免被系统还原，建议先在设置中关闭。</div>

    <!-- 亚服 -->
    <section class="category">
      <button class="category-header" data-target="asia">
        <span>亚服</span><span class="chev">›</span>
      </button>
      <div id="asia" class="category-content">
        <div class="category-content-inner">
          <button class="tzbtn" data-tz="China Standard Time">
            <span class="flag">🇨🇳 🇭🇰</span>
            <span class="label">(UTC+08:00) 北京，重庆，香港特别行政区，乌鲁木齐</span>
          </button>
          <button class="tzbtn" data-tz="Korea Standard Time">
            <span class="flag">🇰🇷</span>
            <span class="label">(UTC+09:00) 首尔</span>
          </button>
          <button class="tzbtn" data-tz="Tokyo Standard Time">
            <span class="flag">🇯🇵</span>
            <span class="label">(UTC+09:00) 大阪，札幌，东京</span>
          </button>
        </div>
      </div>
    </section>

    <!-- 东南亚服 -->
    <section class="category">
      <button class="category-header" data-target="sea">
        <span>东南亚服</span><span class="chev">›</span>
      </button>
      <div id="sea" class="category-content">
        <div class="category-content-inner">
          <button class="tzbtn" data-tz="SE Asia Standard Time">
            <span class="flag">🇹🇭 🇻🇳 🇮🇩</span>
            <span class="label">(UTC+07:00) 曼谷，河内，雅加达</span>
          </button>
          <button class="tzbtn" data-tz="W. Australia Standard Time">
            <span class="flag">🇦🇺</span>
            <span class="label">(UTC+08:00) 珀斯</span>
          </button>
          <button class="tzbtn" data-tz="AUS Eastern Standard Time">
            <span class="flag">🇦🇺</span>
            <span class="label">(UTC+10:00) 堪培拉，墨尔本，悉尼</span>
          </button>
        </div>
      </div>
    </section>

    <!-- 俄服 -->
    <section class="category">
      <button class="category-header" data-target="ru">
        <span>俄服</span><span class="chev">›</span>
      </button>
      <div id="ru" class="category-content">
        <div class="category-content-inner">
          <button class="tzbtn" data-tz="Russian Standard Time">
            <span class="flag">🇷🇺</span>
            <span class="label">(UTC+03:00) 莫斯科，圣彼得堡</span>
          </button>
        </div>
      </div>
    </section>

    <!-- 欧服 -->
    <section class="category">
      <button class="category-header" data-target="eu">
        <span>欧服</span><span class="chev">›</span>
      </button>
      <div id="eu" class="category-content">
        <div class="category-content-inner">
          <button class="tzbtn" data-tz="W. Europe Standard Time">
            <span class="flag">🇳🇱 🇩🇪 🇨🇭 🇮🇹 🇸🇪 🇦🇹</span>
            <span class="label">(UTC+01:00) 阿姆斯特丹，柏林，伯尔尼，罗马，斯德哥尔摩，维也纳</span>
          </button>
          <button class="tzbtn" data-tz="GMT Standard Time">
            <span class="flag">🇮🇪 🏴 🇵🇹 🇬🇧</span>
            <span class="label">(UTC+00:00) 都柏林，爱丁堡，里斯本，伦敦</span>
          </button>
        </div>
      </div>
    </section>

    <!-- 美服 -->
    <section class="category">
      <button class="category-header" data-target="us">
        <span>美服</span><span class="chev">›</span>
      </button>
      <div id="us" class="category-content">
        <div class="category-content-inner">
          <button class="tzbtn" data-tz="Hawaiian Standard Time">
            <span class="flag">🇺🇲</span>
            <span class="label">(UTC-10:00) 夏威夷</span>
          </button>
          <button class="tzbtn" data-tz="Pacific Standard Time">
            <span class="flag">🇺🇸</span>
            <span class="label">(UTC-08:00) 太平洋时间（美国和加拿大）</span>
          </button>
        </div>
      </div>
    </section>

    <div class="footer">程序已以管理员身份运行。若仍然无效，请在 Windows 设置 → 时间和语言 → 日期和时间 中关闭"自动设置时区"。</div>
  </div>

<script>
  // 折叠/展开逻辑 + 动画
  document.querySelectorAll(".category-header").forEach(h => {
    h.addEventListener("click", () => {
      const id = h.getAttribute("data-target");
      const panel = document.getElementById(id);
      const active = h.classList.toggle("active");
      if (active) {
        panel.style.maxHeight = (panel.scrollHeight + 8) + "px";
        panel.style.opacity = "1";
      } else {
        panel.style.maxHeight = "0px";
        panel.style.opacity = "0";
      }
    });
  });

  // 绑定按钮点击 -> Python 后端
  document.querySelectorAll(".tzbtn").forEach(btn => {
    btn.addEventListener("click", async () => {
      const tz = btn.getAttribute("data-tz");
      try {
        const res = await pywebview.api.set_timezone(tz);
        alert(res);
      } catch (e) {
        alert("❌ 无法与后端通信：" + e);
      }
    });
  });

  // 启动检查：自动时区
  (async () => {
    try {
      const autoTz = await pywebview.api.check_auto_tz();
      if (autoTz === "RUNNING") {
        document.getElementById("autoTzWarn").classList.add("show");
      }
    } catch (e) {
      // 忽略
    }
  })();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    # 检查并提升管理员权限
    if not run_as_admin():
        # 如果需要提升权限，程序会重新启动，当前进程退出
        sys.exit(0)
    
    # 程序已以管理员身份运行
    api = Api()
    # 创建窗口时注册 API
    window = webview.create_window("时区切换器", html=HTML, width=680, height=520, js_api=api)
    # 启动窗口，不再传 api
    webview.start(debug=False)
