$(document).ready(function(){
	var ENDPOINT = "/ekatte/data_for_city.html";

	function appendResult(result, to_where){
		console.log(result);
		var para = $("<p />");
		para.html(result.front + " <span style='color: red'>" + result.name + "</span> от община " + result.obstini + " от област " + result.oblast + 
			" създадено с документ " + result.institution + " от " + result.document + ", регион " + result.region + " гоуем регион " + result.big_region);

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
			method: "GET",
			data: data,
			dataType: "json"
		}).then(function(responce){
			var list = $("#results");
			list.html("");
			for (var i = 0; i <= responce.length; i++) {
				appendResult(responce[i], list);
			}
		});
	});
});