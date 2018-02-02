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
    constructor(mapid, startdate, period) {

        $('#graphInfo').slideDown("slow");
        $('#graphInfo').text("Now Loading ...");

        // JSONデータの生成
        gen_jsondata(mapid, startdate, period);

        // グラフの描画準備
        this.options = {
            // 描画エリアの設定
            chartArea: { 'width': '90%', 'height': '75%' },
            // 横ラベル
            hAxis: {
                title: '時間',
                titleTextStyle: { italic: false }
            },
            // 縦ラベル
            vAxis: {
                title: '温度[℃]',
                titleTextStyle: { italic: false },
                viewWindow:{
                    max:35,
                    min:0
                }
            },
            height: 480,
            width:960,
            // カーソルを合わせた時の表示
            crosshair: { trigger: 'both' },
            // カーソルを合わせた時に同じ縦軸のデータをまとめて表示
            focusTarget: 'category',
            // 凡例
            legend: {
                position: 'top',
                maxLines: 2,
                textStyle: {color: 'royalblue', fontSize: 10.5}
            }
        };

        // グラフの描画先を指定
        this.chart = new google.visualization.LineChart(document.getElementById('graphField'));
    }

    /*
     * グラフの再描画
     */
    draw() {
        $('#graphInfo').hide();
        $('#graphInfo').text("");
        $('#graphField').show();

        var json = _jsondata;
        var datatable = new google.visualization.DataTable(json);
        this.chart.draw(datatable, this.options);

    }
}
