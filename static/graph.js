var formatDate = function (date, format) {
    if (!format) format = 'YYYY-MM-DD hh:mm:ss.SSS';
    format = format.replace(/YYYY/g, date.getFullYear());
    format = format.replace(/MM/g, ('0' + (date.getMonth() + 1)).slice(-2));
    format = format.replace(/DD/g, ('0' + date.getDate()).slice(-2));
    format = format.replace(/hh/g, ('0' + date.getHours()).slice(-2));
    format = format.replace(/mm/g, ('0' + date.getMinutes()).slice(-2));
    format = format.replace(/ss/g, ('0' + date.getSeconds()).slice(-2));
    if (format.match(/S/g)) {
        var milliSeconds = ('00' + date.getMilliseconds()).slice(-3);
        var length = format.match(/S/g).length;
        for (var i = 0; i < length; i++) format = format.replace(/S/, milliSeconds.substring(i, i + 1));
    }
    return format;
};

var GraphChg = function ($) {
    Graph.chgStatus(DatePicker.get(), "day", SelectLocation.get(), "p1");
}

var DatePicker = {
    id: null,
    init: function (id) {
        this.id = id;

        $(this.id).datepicker({
            format: 'yyyy/mm/dd',
            language: 'ja',
            autoclose: true,
            clearBtn: true,
            clear: '閉じる',
            onSelect: GraphChg
        });
        $(this.id).datepicker("setDate", "2017/11/22");
    },
    get: function () {
        return $(this.id).datepicker("getDate");
    }
};

var SelectLocation = {
    id: null,
    init: function (id) {
        this.id = id;
        $(this.id).change(GraphChg);
    },
    get: function () {
        return $(this.id).val();
    }
};

var InfoBoard = {
    load: function (id) {
        $(id).slideDown("slow");
        $(id).text("Now Loading ...");
    },
    error: function (id, msg) {
        $(id).slideDown("slow");
        $(id).text("Error: " + msg);
    },
    close: function (id) {
        $(id).slideUp("slow");
        $(id).text("");
    },
};

var Graph = {
    // グラフ 要素ID
    graphid: null,
    // グラフ 描画先
    chart: null,
    // 情報欄 要素ID
    infoid: null,
    // グラフ 開始日
    date: null,
    // グラフ 周期
    period: null,
    // グラフ JSONデータ
    json: null,
    // グラフ オプション
    options: {
        // 描画エリアの設定
        chartArea: { 'width': '90%', 'height': '75%' },
        // 横ラベル
        hAxis: {
            title: '時間',
            titleTextStyle: { italic: false },
        },
        // 縦ラベル
        vAxis: {
            title: '温度[℃]',
            titleTextStyle: { italic: false },
            viewWindow: {
                max: 35,
                min: 0,
            }
        },
        height: 480,
        width: 800,
        // カーソルを合わせた時の表示
        crosshair: { trigger: 'both', orientation: 'vertical' },
        // カーソルを合わせた時に同じ縦軸のデータをまとめて表示
        focusTarget: 'category',
        // 凡例
        legend: {
            position: 'top',
            maxLines: 2,
            textStyle: { color: 'royalblue', fontSize: 10.5 }
        }
    },



    init: function (graphid, infoid) {
        /*
         * グラフの初期設定
         * graphid: グラフの要素ID
         */

        // オプション設定
        this.graphid = graphid;
        this.infoid = infoid;
        $(infoid).hide();
        $(graphid).hide();
        $.when(this.initGoogle()).then(function () {
            Graph.chart = new google.visualization.LineChart(document.getElementById(graphid.slice(1)));
        });
    },



    initGoogle: function () {
        /*
         * Google Chart Toolsの初期設定
         */

        // Google Chart Tools API 読込
        var gct_def = new $.Deferred();
        google.charts.load('current', { 'packages': ['corechart'] });
        google.charts.setOnLoadCallback(function () {
            gct_def.resolve();
        });
        return gct_def.promise();
    },



    chgStatus: function (startdate, period, tag, kind) {
        /*
         * グラフの設定変更
         * @startdate Datatime型 開始日
         * @kind      String型   データ種類
         * @tag       String型   絞り込みタグ
         * @period    String型   表示期間
         */

        // グラフの更新が必要かどうかを判定する
        if (this.startdate == startdate && this.period == period
            && this.kind == kind && this.tag == tag) {

            return;
        }
        this.startdate = startdate;
        this.period = period;
        this.kind = kind;
        this.tag = tag;

        // ロード開始
        InfoBoard.load(this.infoid);
        console.time('graph: total time');
        console.time('graph: load time');

        // グラフのデータを取得
        var dt = this.getJSON(new Date(startdate));

        // 取得が完了したら
        $.when(dt).then(function () {
            console.timeEnd('graph: load time');
            // グラフの描画
            console.time('graph: draw time');
            Graph.draw();
            console.timeEnd('graph: draw time');

            // ロード終了
            console.timeEnd('graph: total time');
        });
    },



    getJSON: function (getdate) {
        /*
         * 日誌の読み込み
         * @date Datatime型 日付
         */

        // 日付が今日ならキャッシュしない
        var cachemode = true;
        var today = new Date();
        if (getdate.getFullYear() == today.getFullYear()
            && getdate.getMonth() == today.getMonth()
            && getdate.getDate() == today.getDate()) {

            cachemode = false;
        }

        var datas = {
            'date': formatDate(getdate, "YYYYMMDD000000"),
            'kind': this.kind,
            'tag': this.tag
        };
        if (this.tag === "none") {
            delete datas.tag;
        }

        // 読み込み
        return $.ajax({
            cache: cachemode,
            dataType: 'jsonp',
            jsonpCallback: 'callback',
            type: 'GET',
            url: url + 'diary',
            data: datas
        }).done(function (json) {
            // JSONを格納
            Graph.json = json;
        });
    },



    draw: function () {
        /*
         * グラフの描画・再描画
         * startdate : 開始日
         * period : 周期
         */
        InfoBoard.close(this.infoid);
        $(this.graphid).show();


        var datatable = new google.visualization.DataTable(this.json);
        var formatter = new google.visualization.DateFormat({ pattern: "y/M/d HH:mm" });
        formatter.format(datatable, 0);
        this.chart.draw(datatable, this.options);
    },
};
