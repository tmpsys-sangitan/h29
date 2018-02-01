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

var _jsondata;

function gen_jsondata(mapid, startdate, period) {
    /*
     * データテーブル用JSON管理クラス
     */

    // JSONの宣言
    this.json = JSON.stringify();

    // データ受信完了待ち
    $.when(
        this.get_diary(new Date(startdate))
    ).then(function () {
        console.log("data done");
        // グラフの描画
        j.draw()
        console.log("complete");
    })
}

function get_diary(date, jd) {
    /*
     * 日誌の読み込み
     * @date Datatime型 日付
     */

    // ディファードの宣言
    var df = new $.Deferred();

    // 日付が今日ならキャッシュしない
    var cachemode = true;
    var today = new Date();
    if (date.getFullYear() == today.getFullYear()
        && date.getMonth() == today.getMonth()
        && date.getDate() == today.getDate()) {

        cachemode = false;
    }

    // 読み込み
    $.ajax({
        cache: cachemode,
        dataType: 'jsonp',
        jsonpCallback: 'callback',
        type: 'GET',
        url: url + 'diary',
        data: {
            'date': formatDate(date, "YYYYMMDD000000")
        }
    }).done(function (json) {
        // JSONを格納
        _jsondata = json;

        // プロミスを更新
        df.resolve();
    });

    // プロミスを返す
    return df.promise();
}
