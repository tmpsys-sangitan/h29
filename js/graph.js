// Google Chart Tools API 読込
google.load('visualization', '1.0', { 'packages': ['corechart'] });

/*
 * グラフの描画クラス
 */
class Graph {
    /*
     * コンストラクタ
     * グラフの基本情報定義
     */
    constructor(label, mapid, startdate, period) {

        // JSONデータの生成
        gen_jsondata(label, mapid, startdate, period);

        // グラフの描画準備
        this.options = {
            // タイトル
            title: '気温グラフ',
            // タイトルのフォント設定
            titleTextStyle: { fontName: 'Meiryo', fontSize: 30 },
            // 描画エリアの設定
            chartArea: { 'width': '90%', 'height': '65%' },
            // 横ラベル
            hAxis: {
                title: '時間',
                titleTextStyle: { italic: false }
            },
            // 縦ラベル
            vAxis: {
                title: '温度',
                titleTextStyle: { italic: false },
                viewWindow:{
                    max:30,
                    min:0
                }
            },
            // カーソルを合わせた時の表示
            crosshair: { trigger: 'both' },
            // カーソルを合わせた時に同じ縦軸のデータをまとめて表示
            focusTarget: 'category',
            // 凡例
            legend: { position: 'bottom' }
        };

        // グラフの描画先を指定
        this.chart = new google.visualization.LineChart(document.getElementById('graphField'));
    }

    /*
     * グラフの再描画
     */
    draw() {
        var json = _jsondata;
        console.log(_jsondata);
        var datatable = new google.visualization.DataTable(json);
        this.chart.draw(datatable, this.options);
    }
}
