// グラフ再描画関数
var graph_draw;

// グラフ初期設定
function init_graph(data) {
    var data;       // データ
    var options;    // 描画オプション
    var chart;      // グラフオブジェクト

    // Google Chart Tools API 読込
    google.load('visualization', '1.0', { 'packages': ['corechart'] });

    google.setOnLoadCallback(
        function () {
            // データの格納
            data = google.visualization.arrayToDataTable(data);

            // グラフの描画オプション
            options = {
                // タイトル
                title: '気温グラフ',
                // タイトルのフォント設定
                titleTextStyle: { fontName: 'Meiryo', fontSize: 30},
                // 描画エリアの設定
                chartArea: { 'width': '90%', 'height': '65%'},
                // 横ラベル
                hAxis: {
                    title: '時間',
                    titleTextStyle: { italic: false }
                },
                // 縦ラベル
                vAxis: { title: '温度', titleTextStyle: { italic: false } },
                // カーソルを合わせた時の表示
                crosshair: { trigger: 'both' },
                // カーソルを合わせた時に同じ縦軸のデータをまとめて表示
                focusTarget: 'category',
                // 凡例
                legend: {
                    position: 'bottom'
                }
            };

            // 描画先IDを指定
            chart = new google.visualization.LineChart(document.getElementById('graphField'));
            // グラフ描画
            chart.draw(data, options);
        }
    );

    // グラフ再描画
    graph_draw = function(){
        chart.draw(data, options);
    }
}

// ウィンドウリサイズ時にグラフ再描画
window.onresize = function () {
    graph_draw();
}
