from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import threading
import time
import json
import os
from datetime import datetime
import pynput
from pynput import mouse, keyboard
from pynput.mouse import Button, Listener as MouseListener
from pynput.keyboard import Key, Listener as KeyboardListener
import queue

app = Flask(__name__)
CORS(app)

class MouseRecorder:
    def __init__(self):
        self.recording = False
        self.recorded_actions = []
        self.start_time = None
        self.mouse_listener = None
        self.keyboard_listener = None
        self.replay_thread = None
        self.replaying = False
        self.replay_loop = False
        
        # 启动全局键盘监听器用于快捷键
        self.start_keyboard_listener()
        
    def start_keyboard_listener(self):
        """启动全局键盘监听器"""
        def on_key_press(key):
            try:
                # Ctrl+Shift+R 开始/停止录制
                if hasattr(key, 'char') and key.char == 'r':
                    # 检查是否同时按下了Ctrl和Shift（这个检测在pynput中比较复杂，我们简化处理）
                    pass
                elif key == Key.f9:  # F9键开始/停止录制
                    if not self.recording:
                        self.start_recording()
                        print("⚫ 快捷键启动录制")
                    else:
                        self.stop_recording()
                        filepath = self.save_recording()
                        print(f"⏹️ 快捷键停止录制，已保存到: {filepath}")
                elif key == Key.f10:  # F10键开始/停止回放
                    if not self.replaying:
                        if self.recorded_actions:
                            self.replay_actions(loop=False)
                            print("▶️ 快捷键启动回放")
                    else:
                        self.stop_replay()
                        print("⏹️ 快捷键停止回放")
                elif key == Key.f11:  # F11键开始/停止循环回放
                    if not self.replaying:
                        if self.recorded_actions:
                            self.replay_actions(loop=True)
                            print("🔄 快捷键启动循环回放")
                    else:
                        self.stop_replay()
                        print("⏹️ 快捷键停止循环回放")
            except AttributeError:
                pass
        
        def on_key_release(key):
            pass
        
        self.keyboard_listener = KeyboardListener(
            on_press=on_key_press,
            on_release=on_key_release
        )
        self.keyboard_listener.daemon = True
        self.keyboard_listener.start()
        
    def start_recording(self):
        """开始录制鼠标操作"""
        if self.recording:
            return False
            
        self.recording = True
        self.recorded_actions = []
        self.start_time = time.time()
        
        # 启动鼠标监听器
        self.mouse_listener = MouseListener(
            on_move=self.on_mouse_move,
            on_click=self.on_mouse_click,
            on_scroll=self.on_mouse_scroll
        )
        self.mouse_listener.start()
        return True
    
    def stop_recording(self):
        """停止录制鼠标操作"""
        if not self.recording:
            return False
            
        self.recording = False
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        return True
    
    def on_mouse_move(self, x, y):
        """鼠标移动事件"""
        if self.recording:
            current_time = time.time() - self.start_time
            action = {
                'type': 'move',
                'x': x,
                'y': y,
                'timestamp': current_time
            }
            self.recorded_actions.append(action)
    
    def on_mouse_click(self, x, y, button, pressed):
        """鼠标点击事件"""
        if self.recording:
            current_time = time.time() - self.start_time
            action = {
                'type': 'click',
                'x': x,
                'y': y,
                'button': str(button),
                'pressed': pressed,
                'timestamp': current_time
            }
            self.recorded_actions.append(action)
    
    def on_mouse_scroll(self, x, y, dx, dy):
        """鼠标滚轮事件"""
        if self.recording:
            current_time = time.time() - self.start_time
            action = {
                'type': 'scroll',
                'x': x,
                'y': y,
                'dx': dx,
                'dy': dy,
                'timestamp': current_time
            }
            self.recorded_actions.append(action)
    
    def save_recording(self, filename=None):
        """保存录制的操作到文件"""
        if not self.recorded_actions:
            return False
            
        if filename is None:
            filename = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # 确保recordings目录存在
        recordings_dir = "recordings"
        if not os.path.exists(recordings_dir):
            os.makedirs(recordings_dir)
        
        filepath = os.path.join(recordings_dir, filename)
        
        data = {
            'actions': self.recorded_actions,
            'total_duration': self.recorded_actions[-1]['timestamp'] if self.recorded_actions else 0,
            'created_at': datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def load_recording(self, filepath):
        """从文件加载录制的操作"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.recorded_actions = data['actions']
            return True
        except Exception as e:
            print(f"加载录制文件失败: {e}")
            return False
    
    def replay_actions(self, loop=False):
        """回放录制的操作"""
        if not self.recorded_actions or self.replaying:
            return False
        
        self.replaying = True
        self.replay_loop = loop
        
        def replay_thread():
            mouse_controller = pynput.mouse.Controller()
            
            while self.replaying:
                try:
                    last_timestamp = 0
                    
                    for action in self.recorded_actions:
                        if not self.replaying:
                            break
                        
                        # 等待到指定时间
                        wait_time = action['timestamp'] - last_timestamp
                        if wait_time > 0:
                            time.sleep(wait_time)
                        
                        # 执行操作
                        if action['type'] == 'move':
                            mouse_controller.position = (action['x'], action['y'])
                        
                        elif action['type'] == 'click':
                            mouse_controller.position = (action['x'], action['y'])
                            button = Button.left if 'left' in action['button'] else Button.right
                            if action['pressed']:
                                mouse_controller.press(button)
                            else:
                                mouse_controller.release(button)
                        
                        elif action['type'] == 'scroll':
                            mouse_controller.position = (action['x'], action['y'])
                            mouse_controller.scroll(action['dx'], action['dy'])
                        
                        last_timestamp = action['timestamp']
                    
                    # 如果不是循环模式，结束回放
                    if not self.replay_loop:
                        self.replaying = False
                    else:
                        # 循环模式下，添加一个短暂的延迟再开始下一轮
                        time.sleep(1)
                        
                except Exception as e:
                    print(f"回放过程中发生错误: {e}")
                    self.replaying = False
        
        self.replay_thread = threading.Thread(target=replay_thread)
        self.replay_thread.daemon = True
        self.replay_thread.start()
        return True
    
    def stop_replay(self):
        """停止回放"""
        self.replaying = False
        self.replay_loop = False
    
    def get_recordings_list(self):
        """获取保存的录制文件列表"""
        recordings_dir = "recordings"
        if not os.path.exists(recordings_dir):
            return []
        
        recordings = []
        for filename in os.listdir(recordings_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(recordings_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    recordings.append({
                        'filename': filename,
                        'filepath': filepath,
                        'duration': data.get('total_duration', 0),
                        'actions_count': len(data.get('actions', [])),
                        'created_at': data.get('created_at', '')
                    })
                except:
                    continue
        
        return sorted(recordings, key=lambda x: x['created_at'], reverse=True)

# 创建全局录制器实例
recorder = MouseRecorder()

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/api/start_recording', methods=['POST'])
def start_recording():
    """开始录制API"""
    if recorder.start_recording():
        return jsonify({'success': True, 'message': '开始录制鼠标操作'})
    else:
        return jsonify({'success': False, 'message': '录制已在进行中'})

@app.route('/api/stop_recording', methods=['POST'])
def stop_recording():
    """停止录制API"""
    if recorder.stop_recording():
        # 自动保存录制
        filepath = recorder.save_recording()
        return jsonify({
            'success': True, 
            'message': '录制已停止并保存',
            'filepath': filepath,
            'actions_count': len(recorder.recorded_actions)
        })
    else:
        return jsonify({'success': False, 'message': '没有正在进行的录制'})

@app.route('/api/replay', methods=['POST'])
def replay():
    """回放录制API"""
    data = request.get_json()
    loop = data.get('loop', False)
    
    if recorder.replay_actions(loop=loop):
        return jsonify({'success': True, 'message': f'开始回放{"（循环模式）" if loop else ""}'})
    else:
        return jsonify({'success': False, 'message': '没有可回放的录制或正在回放中'})

@app.route('/api/stop_replay', methods=['POST'])
def stop_replay():
    """停止回放API"""
    recorder.stop_replay()
    return jsonify({'success': True, 'message': '回放已停止'})

@app.route('/api/status', methods=['GET'])
def get_status():
    """获取状态API"""
    return jsonify({
        'recording': recorder.recording,
        'replaying': recorder.replaying,
        'replay_loop': recorder.replay_loop,
        'actions_count': len(recorder.recorded_actions)
    })

@app.route('/api/recordings', methods=['GET'])
def get_recordings():
    """获取录制文件列表API"""
    recordings = recorder.get_recordings_list()
    return jsonify({'recordings': recordings})

@app.route('/api/load_recording', methods=['POST'])
def load_recording():
    """加载录制文件API"""
    data = request.get_json()
    filepath = data.get('filepath')
    
    if recorder.load_recording(filepath):
        return jsonify({
            'success': True, 
            'message': '录制文件加载成功',
            'actions_count': len(recorder.recorded_actions)
        })
    else:
        return jsonify({'success': False, 'message': '加载录制文件失败'})

if __name__ == '__main__':
    print("鼠标操作录制系统启动中...")
    print("请在浏览器中打开: http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
