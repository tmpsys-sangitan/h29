/*
 * 日誌の読み込み
 * @date Datatime型 日付
 */
function read_diary(date, mapid, type, jd) {
    // ディファードの宣言
    var df = new $.Deferred();

    // URL生成
    var url = 'http://tmpsys-sangitan.appspot.com/diary';

    // 日付が今日ならキャッシュしない
    var cachemode = true;
    var today = new Date();
    if (date.getFullYear() == today.getFullYear()
            && date.getMonth() == today.getMonth()
            && date.getDate() == today.getDate()){

        cachemode = false;
    }

    // 読み込み
    $.ajax({
        ajax: false,
        cache: cachemode,
        dataType: 'jsonp',
        jsonpCallback: 'callback',
        type: 'GET',
        url  : url,
        data : {
            'date' : formatDate(date, "YYYYMMDD"),
            'mapid': mapid,
            'type' : type
        }
    }).done(function(json, type){
        console.log(jd.json);
        // JSONを元にjdを書き換え
        var end_date = new Date(date);
        end_date.setDate(end_date.getDate() + 1);
        for (var d = new Date(date); d < end_date; d.setMinutes(d.getMinutes() + 1)) {
            var val = json[formatDate(d, "hhmm")].val;

            jd.add_data(d, mapid, val);
        }

        // グラフの再描画
        j.draw();

        // プロミスを更新
        df.resolve();
    });

    // プロミスを返す
    return df.promise();
}
