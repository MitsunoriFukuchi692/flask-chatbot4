$(function (){
	//共通エリア
	let root;
	let scripts = document.getElementsByTagName('script');
	let i = scripts.length;
	while (i--) {
		const match = scripts[i].src.match(/(^|.*\/)common\.min\.js$/);
		if (match) {
			root = match[1];
			break;
		}
	}
	const sitePath =  root.replace('js/','');
	const includeFileName = 'include.html';
	$.ajax({
		type: 'GET',
		url: sitePath+includeFileName,
		dataType: 'html',
	})
	.then(
		function(data){
			data = data.replace( /href="\//g , 'href="'+sitePath );
			data = data.replace( /src="\//g , 'src="'+sitePath );
			const navInc1 = $('<div/>').html(data).find('.nav');
			$('#navInc1').append(navInc1);
			const navInc2 = $('<div/>').html(data).find('.nav--wrap');
			$('#navInc2').append(navInc2);
			const footerInc = $('<div/>').html(data).find('#footer');
			$('#footerInc').append(footerInc);
			includeOpen();
		}
	);

	//link
	if($(".icon-blank").length){
		$(".icon-blank").append('<span>');
	}
	if($(".icon-arrow").length){
		$(".icon-arrow").append('<span>');
	}

	//heading
	if(!$('body#home').length){
		const heading = $('#heading h2');
		heading.each(function(){
			var text = $(this).text();
			var textbox = "";
			text.split('').forEach(function (t, i) {
				if (t !== " ") {
					var n = i * 50;
					var m = n + 800;
					textbox += '<span style="animation-delay:' + m + 'ms;">' + t + '</span>';
				} else {
					textbox += t;
				}
			});
			$(this).html(textbox);
		});
	}
});


function includeOpen(){
	//scroll event
	const header = $('#navInc2');
	$(window).on('scroll', function() {
		const scrT = $(window).scrollTop();
		const headingH = $('#heading').outerHeight();
		if(scrT > headingH + 100) {
			header.addClass('fix');
		} else {
			header.removeClass('fix');
		}
	});

	//nav
	const gnavBtn = $('.navBtn');
	const gnavLis = $('.nav--list');
	gnavBtn.append('<span></span><span></span><span></span>');
	gnavBtn.on('click', function(){
		gnavBtn.toggleClass('on');
		gnavLis.toggleClass('on');
	});
	gnavLis.find('a').on('click', function(){
		gnavBtn.removeClass('on');
		gnavLis.removeClass('on');
	});

	const logo = $('#header h1').html();
	$('#navInc2').prepend('<div class="headerLogo">'+ logo +'</div>');
}

