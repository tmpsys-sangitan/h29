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

/*
 * データテーブル用JSON管理クラス
 */
class Jsondata {
    /*
     * コンストラクタ
     * JSONの雛形作成
     */
    constructor(label, mapid, startdate, period) {

        // JSONの宣言
        this.json = {
            'cols': [
                {
                    'label': "日時",
                    'type': "datetime"
                }
            ],
            'rows': []
        };

        // ヘッターの設定
        this.label_list = label.concat();
        this.mapid_list = mapid.concat();
        for (var i = 0; i < label_list.length; i++) {
            this.add_header(label_list[i], mapid_list[i]);
        }

        // 空データの設定
        var end_date = new Date(startdate);
        end_date.setDate(end_date.getDate() + 1);
        for (var d = new Date(startdate); d < end_date; d.setMinutes(d.getMinutes() + 1)) {
            this.add_nonedata(d);
        }

        // データの設定
        var date = new Date("2017/11/22 00:00:00 +0900")
        for (var i = 0; i < mapid_list.length; i++) {
            read_diary(date, mapid_list[i], "temp", this)
        }


    }

    /*
     * ヘッターの追加
     */
    add_header(labels, mapid) {

        // ヘッターに追加するオブジェクトの作成
        var new_herder = {
            'id': mapid,
            'label': labels,
            'type': "number"
        };
        this.json.cols.push(new_herder);
    }

    /*
     * 空データの追加
     */
    add_nonedata(date) {

        // ボディに追加する空データの作成
        var new_data = {
            'c': [
                { 'v': formatDate(date, "Date(YYYY, MM, DD, hh, mm, ss)") }
            ]
        };

        // 空データにヘッタの数だけNoneを追加
        for (var i = 0; i < this.label_list.length; i++) {
            new_data.c.push({
                'v': null
            });
        }
        this.json.rows.push(new_data);

    }

    /*
     * データの置き換え
     */
    add_data(date, mapid, val) {

        // 対応する時間軸の検索
        var newLines = this.json.rows.filter(function(item, index){
            if ((item.c[0].v).indexOf(formatDate(date, "Date(YYYY, MM, DD, hh, mm, ss)")) >= 0) return true;
        });

        // 対応するセンサの検索
        var idx = this.mapid_list.indexOf(mapid) + 1

        // 書き換え
        newLines[0].c[idx].v = val;

    }
}