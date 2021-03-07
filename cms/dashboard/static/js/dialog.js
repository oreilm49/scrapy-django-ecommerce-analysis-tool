
// Commonly used buttons that do nothing
var BTN_CANCEL = button(gettext('Cancel'), 'glyphicon-remove');
var BTN_OK = button(gettext('OK'), 'glyphicon-ok');

function button(label, icon, action) {
    return {label: label, icon: icon, action: action}
}

function linkButton(label, icon, url) {
    return {label: label, icon: icon, url: url}
}

function btnRemove(actionOrUrl) {
    if (typeof actionOrUrl === 'string' || actionOrUrl instanceof String) actionOrUrl = urlAction(actionOrUrl);
    return button(gettext('Remove'), 'glyphicon-trash', actionOrUrl);
}

function btnSave(action) {
    return button(gettext('Save'), 'glyphicon-ok', action);
}

function urlAction(url) {
    return function () {
        window.location = url;
    };
}

function showDialog(title, body, btnSuccess, btnPrimary, btnDanger) {
    var dialog = $('#dialog');
    if (dialog.length === 0) {
        console.error('Cannot find #dialog. Make sure that dialog.html template is included.');
        return;
    }
    dialog.find('.modal-title').text(title);
    dialog.find('.modal-body>p').html(body);

    [
        ['button#btn-danger', btnDanger],
        ['button#btn-primary', btnPrimary],
        ['button#btn-success', btnSuccess],
    ].forEach(function (value) {
        var selector = value[0];
        var btnData = value[1];
        var button = dialog.find(selector);
        if (!btnData) button.hide();
        else {
            // unbind any previous listener
            button.unbind('click');
            var btnIcon = button.find('#btn-icon');
            if (btnData.icon) {
                if (btnData.icon.indexOf('glyphicon-') < 0) btnData.icon = 'glyphicon-' + btnData.icon;
                btnIcon.removeClass(function (index, className) {
                    return (className.match(/(^|\s)glyphicon-\S+/g) || []).join(' ');
                });
                btnIcon.addClass(['glyphicon', btnData.icon]);
                btnData.label = ' ' + btnData.label;
            } else btnIcon.attr('class', '');
            button.find('#btn-label').text(btnData.label);
            if (btnData.url) btnData.action = urlAction(btnData.url);
            if (btnData.action) {
                button.click(btnData.action);
            } else
                button.unbind('click');
            button.show();
        }
    });
    dialog.modal();
}

$(document).ready(function () {
    // For for Internet Explorer: anchortags not having a href do not handle onclick
    $('a[onclick]:NOT([href])').attr('href', '#');
});
