
function vigiboard_shndialog(url,idd) {
	$.getJSON(url+'get_plugin_value',{plugin_name:'shn',idaggregate:idd},function(json){ 				
		var ht = '';
		for (var i = 0; i < json.shns.length; i++) {
			ht += '<li>' + json.shns[i] + '</li>';
		}
		$('#SHNDialog_liste').html(ht);
		$('#SHNDialog').dialog('open');
	})
}
$('.SHNLien').each(function() {
	$(this).click(function(e){
	$('#SHNDialog').dialog('option','position',[e.clientX+10,e.clientY]);
	})});
