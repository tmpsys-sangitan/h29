var Clock = {
    get: function(id){
        $(id).text(formatDate(new Date(), "YYYY/MM/DD hh:mm:ss"));
    }
};

var HeatMap = {

    init: function(){
        this.getLatest("p1")
    },

    getLatest: function(kind){
        /*
         * 最新温度データの取得
         * kind : 取得したいマップIDの配列
         */
        return $.ajax({
            cache: false,
            dataType: 'jsonp',
            jsonpCallback: 'callback',
            type: 'GET',
            url: url + 'latest',
            data: {
                'kind': kind
            }
        }).done(function (json){
            HeatMap.searchSensor(json);
        });
    },



    searchSensor: function(latest_json){
        /*
         * searchSensor .snsrクラスを検索して温度の表示と背景色の変更を行う
         * latest_json : 最新温度データのJSON
         */

        jQuery('.snsr').each(function(){
            var temp = latest_json[$(this).attr('class').split(' ')[1]]
            if (temp != null) {
                HeatMap.setNewlabel(this, temp);
                HeatMap.setBGColor(this, temp);
            }
        });
    },



    setNewlabel: function(id, temp){
        /*
         * setNewlabel 温度とラベルを表示
         * id : 変更する要素
         * temp : 温度
         */
        $(id).html($(id).text() + "<br>" + temp + "℃");
    },



    setBGColor: function(id, temp){
        /*
         * setBGColor 温度に応じて指定された要素の背景色を変更する
         * id : 変更する要素
         * temp : 温度
         */
        $(id).css('background-color', hsv(220-220*temp/35, 0.5, 1));
    }
}

function hsv(h,s,v){
    /*
     * HSV色値をRGBカラーコードに変換する
     */
    var f=h/60,i=f^0,m=v-v*s,k=v*s*(f-i),p=v-k,q=k+m;
    return '#'+c16([v,p,m,m,q,v][i]*255^0)+c16([q,v,v,p,m,m][i]*255^0)+c16([m,m,q,v,v,p][i]*255^0);
}

function c16( c10 ){
    /*
     * 10進数を16進数に変換する
     */
    var c16 = '0'+c10.toString(16);
    return c16.substr(c16.length-2);
}
