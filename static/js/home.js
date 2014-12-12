window.addEvent('domready', function() {
	'use strict';

	$$('form')[0].addEvent('submit', function(e) {
		e.preventDefault();
		var form = e.target;
		var character = form.getElement('input[name="char"]').get('value');
		var password = form.getElement('input[name="pass"]').get('value');
		character = character.replace(' ', '_');
		var url = window.location.origin + '/skillcheck/' + character;
		if (password)
			url += '?pass=' + encodeURIComponent(password)
		window.location = url;
	});
});
