$(document).ready(function(){
	var ENDPOINT = "/ekatte/data_for_city.php";

	function appendResult(result, to_where){
		console.log(result);
		var para = $("<p />");
		para.html(result[1] + " <span style='color: red'>" + result[0] + "</span> от община " + result[3] + " от област " + result[2] + 
			" създадено с документ " + result[5] + " от " + result[4] + " регион " + result[6] + " гоуем регион " + result[7]);

		to_where.append(para);
	}

	$("#checker").change(function(){
		var val = $(this).val();
		if (val.length < 2){
			return;
		}
		var data = {"city": val};

		var createPromise = $.ajax({
			url: ENDPOINT,
			method: "POST",
			data: data
		}).then(function(responce){
			var result_data = JSON.parse(responce)

			var list = $("#results");
			list.html("");
			for (result in result_data){
				appendResult(result_data[result], list);
			}
		});
	});
});