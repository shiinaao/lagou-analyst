function raiser(fn){
    return function (error, data){
        if (error){
            throw new Error(error);
        }
        fn(data);
    }
}

function plot_pie_chart(json_path, bindto){
    function _plot(data){
        var pie_chart = c3.generate({
            bindto: bindto,
            data: {
                json: data,
                type: 'pie'
            }
        });

    }
    d3.json(json_path, raiser(_plot));
}