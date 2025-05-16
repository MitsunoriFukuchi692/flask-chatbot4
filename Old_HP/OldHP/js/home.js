$(function (){
	//#robots
	$('.robot--list a').append('<span class="icon">');


	//一文字ずつ--メインビジュアル用
	const mojiHeading = $('.mojiH');
	mojiHeading.each(function(){
		var text = $(this).text();
		var textbox = "";
		text.split('').forEach(function (t, i) {
			if (t !== " ") {
				var m = i * 40;
				textbox += '<span class="mojiH2"><span style="animation-delay:' + m + 'ms;">' + t + '</span></span>';
			} else {
				textbox += t;
			}
		});
		$(this).html(textbox);
	});
	//一文字ずつ--コンテンツ用
	const moji = $('.moji');
	moji.each(function(){
		var text = $(this).text();
		var textbox = "";
		text.split('').forEach(function (t, i) {
			if (t !== " ") {
				var n = i * 30;
				var m = n + 400;
				textbox += '<span style="animation-delay:' + m + 'ms;">' + t + '</span>';
			} else {
				textbox += t;
			}
		});
		$(this).html(textbox);
	});

	
	//animetion
	setTimeout(() => {
		$('#heading').addClass('on');
	}, 1000);


	//scroll
	const technology = $('#technology');
	const solution = $('#solution');
	const robots = $('#robots');
	const sns = $('#sns');
	$(window).on('scroll', function() {
		const scrT = $(window).scrollTop();
		const scrB = scrT + $(window).height();
		const solutionT = solution.offset().top;
		const robotsT = robots.offset().top;
		const snsT = sns.offset().top;
		if (scrT > 200) {
			technology.addClass('on');
		}
		if (scrB > solutionT + 200) {
			solution.addClass('on');
		}
		if (scrB > robotsT + 200) {
			robots.addClass('on');
		}
		if (scrB > snsT + 200) {
			sns.addClass('on');
		}

		const scrFix = $(this).scrollTop();		
		$('#bg').css('top', parseInt( -scrFix / 7) + 'px');
	});

});
