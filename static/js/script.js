// JavaScriptは極力使わないという要件ですが、
// 動的な部分をすべてPythonで処理するとユーザー体験が損なわれるため、
// 以下の部分のみJavaScriptを使用します。
// 1. 服用タップ時の非同期通信
// 2. 日付タップ時の登録・編集画面の動的表示
// 3. 音の再生（ブラウザのセキュリティ制約のため）
// 4. 通知の表示
// 5. フォーム表示の切り替え

document.addEventListener('DOMContentLoaded', () => {
    // 服用ボタンのクリックイベント
    document.querySelectorAll('.medicine-item').forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault(); // フォームの送信を防止

            const form = button.closest('form');
            const formData = new FormData(form);

            fetch(form.action, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // クラスをトグルして見た目を変更
                    button.classList.toggle('taken', data.is_taken);
                } else {
                    console.error('更新失敗:', data.message);
                }
            })
            .catch(error => {
                console.error('通信エラー:', error);
            });
        });
    });

    // 日付セルをタップして右側のパネルを更新
    document.querySelectorAll('.day-cell').forEach(dayCell => {
        dayCell.addEventListener('click', (event) => {
            const date = dayCell.dataset.date;
            if (date) { // 有効な日付セルのみ
                updateManageSection(date);
            }
        });
    });
    
    // 新規登録ボタンのクリックイベント
    document.addEventListener('click', (event) => {
        if (event.target.id === 'new-medicine-btn') {
            const date = event.target.dataset.date;
            fetchManageForm(date, null, true); // 新規登録フラグをtrueにする
        }
    });

    // 登録済みの薬をタップして編集画面を表示
    document.addEventListener('click', (event) => {
        if (event.target.classList.contains('edit-medicine-link')) {
            event.preventDefault();
            const medicineId = event.target.dataset.medicineId;
            const date = event.target.dataset.date;
            fetchManageForm(date, medicineId);
        }
    });

    // フォーム表示をキャンセル
    document.addEventListener('click', (event) => {
        if (event.target.id === 'form-cancel-btn') {
            const date = event.target.closest('form').querySelector('input[name="date"]').value;
            updateManageSection(date); // 登録・編集フォームを閉じて、その日の薬リストに戻す
        }
    });
    
    // 右側のパネルの内容を更新する
    function updateManageSection(date) {
        const container = document.getElementById('manage-section-container');
        let url = `/medicine_manage_content?date_str=${date}`;

        fetch(url)
            .then(response => response.text())
            .then(html => {
                container.innerHTML = html;
            })
            .catch(error => console.error('Error fetching form:', error));
    }

    // フォームを取得して表示する
    function fetchManageForm(date, medicineId = null, isNew = false) {
        const container = document.getElementById('manage-section-container');
        let url = `/medicine_manage_content?date_str=${date}`;
        if (medicineId) {
            url += `&medicine_id=${medicineId}`;
        }
        if (isNew) {
            url += `&new=true`;
        }
        
        fetch(url)
            .then(response => response.text())
            .then(html => {
                container.innerHTML = html;
            })
            .catch(error => console.error('Error fetching form:', error));
    }


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
