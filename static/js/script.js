// JavaScriptは極力使わないという要件ですが、
// 動的な部分をすべてPythonで処理するとユーザー体験が損なわれるため、
// 以下の部分のみJavaScriptを使用します。
// 1. 服用タップ時の非同期通信
// 2. 音の再生（ブラウザのセキュリティ制約のため）
// 3. 通知の表示

document.addEventListener('DOMContentLoaded', () => {
    // 服用チェックボックスのクリックイベント
    document.querySelectorAll('.medicine-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', (event) => {
            const form = event.target.closest('form');
            const formData = new FormData(form);

            fetch(form.action, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // リンクに`taken`クラスをトグルして見た目を変更
                    const link = form.nextElementSibling;
                    link.classList.toggle('taken', data.is_taken);
                } else {
                    console.error('更新失敗:', data.message);
                }
            })
            .catch(error => {
                console.error('通信エラー:', error);
            });
        });
    });

    // 5分ごとに通知をチェックする
    setInterval(checkNotifications, 300000); // 300000ms = 5分
    checkNotifications(); // 初回起動時にもチェック

    function checkNotifications() {
        fetch('/check_notifications')
            .then(response => response.json())
            .then(data => {
                const notificationArea = document.querySelector('.notification-area');
                if (data.play_sound) {
                    const audio = new Audio('/static/sounds/alarm.mp3');
                    audio.play();

                    notificationArea.innerHTML = '';
                    data.notifications.forEach(notification => {
                        const message = document.createElement('p');
                        message.textContent = `${notification.take_time}に「${notification.name}」を${notification.dosage}服用する時間です。`;
                        notificationArea.appendChild(message);
                    });

                    notificationArea.style.display = 'block';
                    
                    // 10秒後に通知を非表示にする
                    setTimeout(() => {
                        notificationArea.style.display = 'none';
                    }, 10000);
                }
            })
            .catch(error => {
                console.error('通知チェックエラー:', error);
            });
    }
});
