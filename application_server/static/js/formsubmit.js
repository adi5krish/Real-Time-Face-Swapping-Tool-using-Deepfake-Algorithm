function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});


function notifyServerError() {
    toastr.error(gettext('Error occurred. Refresh the page and try again.'))
}

;(function ($, window, document, undefined) {
    // updated to use server responses of 200,400,500
    // using django backend, use something like the following for error / success messages
    // also made it as a jQuery plugin
    //
    // def form_valid(self, form):
    //     data = {
    //         'message': force_text(_('Product added to cart'))
    //     }
    //     return JsonResponse(data)
    //
    // def form_invalid(self, form):
    //     data = {
    //         'errors': form.errors_as_dict()
    //     }
    //     return JsonResponse(data, status=400)
    var pluginName = 'DjangoAjaxHandler2';
    var defaults = {
        container: $('body'),
        formSets: '', // specify form element placeoholder of the formset, we cannot have more form tags inside a form so replace it
        formSetItem: 'tbody tr', // formset table row selector, only used when formSets is specified
        captchaField: '#div_id_captcha', // the holder for the google captcha ... used for error message
        fieldHolder: '.form-group', // specify the field block holder where we can manipulate the field error messages
        removeErrors: function (form, instance) { // error remover before submit
            $(form).find('.has-error').each(function (item) {
                if (!$('div.help-block', item).hasClass('no-delete')) {
                    // we will remove the known error holders which are replaced, the custom ones we leave
                    $('div.help-block', item).remove();
                }
            }).removeClass('has-error');
            if (!$.isEmptyObject(instance.options.errorHolders)) {
                //clear all other predefined error holders
                var classes = $.map(instance.options.errorHolders, function (v, k) {
                    return v;
                }).join();
                $(form).find(classes).text('');
                $(form).find('.help-block').text('');
            }
        },
        processErrors: null, // define as function(form, payload){} to process errors
        afterResponse: null, // define as function(form, payload){} to reload captcha
        beforeSubmission: function (form, instance) { // after errors are cleared, preprocessing can be done here
            $(instance.options.submitBtn).val('loading').prop('disabled', true).addClass('disabled');
            ;
        },
        canSubmit: function (form, instance) { // hook here to interrupt the submission process
            return true;
        },
        onSuccess: function (form, response) {// response from server is 200
            Materialize.toast(response['message'], 5000, 'green accent-4');
            if (response['redirect_url']) {
                setTimeout(function () {
                    window.location.href = response['redirect_url']
                }, 1500)
            }
        },
        postSuccess: function (form, response, instance) {
            form.reset();
            Materialize.updateTextFields();
            $(instance.options.submitBtn).hide('slow');
            $(form).hide('slow');
            $('.message').html(response['message'])
        },
        resetSubmitEvents: true,
        errorHolders: {} // key:value pairs. used for placing the error message in a custom holder near the field used mainly for checkboxes / radio
        /*
        in this example we define a new custom error holder .error-holder.help-block.no-delete
        .no-delete will tell clear function not to remove the element only clear it
        <div class="form-group interest">
            <h5> {% if field.label %}{{ field.label }}{% endif %}</h5>
            <ul class="vertical-list">
                {% for f in field %}
                    <li>
                        <div class="checkbox"><label>
                            <input id="{{ f.id_for_label }}" type="checkbox" name="{{ f.name }}"
                                   value="{{ f.choice_value }}" {% if f.choice_value in field.value %}checked{% endif %}><span>{{ f.choice_label }}</span></label>
                        </div>
                    </li>
                {% endfor %}
            </ul>
            <div class="error-message help-block no-delete"></div>
        </div>
        */
    };

    $.fn.attrs = function () {
        if (arguments.length === 0) {
            if (this.length === 0) {
                return null;
            }

            var obj = {};
            $.each(this[0].attributes, function () {
                if (this.specified) {
                    obj[this.name] = this.value;
                }
            });
            return obj;
        }
    };

    function Plugin(element, options) {
        this.options = $.extend({}, defaults, options);
        this._defaults = defaults;
        this.form = element;
        this._name = pluginName;
        this.init();
    }

    Plugin.prototype.init = function () {

        var instance = this;

        instance.reload = function () {
            //reload form from form_selector
            instance.form = $(instance.options.form_selector)[0];
        }

        var performSubmit = function (e) {
            if (instance.options.resetSubmitEvents)
                e.preventDefault();
            instance.options.removeErrors(instance.form, instance);
            instance.options.beforeSubmission(instance.form, instance);
            if (instance.options.canSubmit(instance.form, instance))
                submit();
        };

        var submit = function () {
            $.ajax({
                url: $(instance.form).attr('action'),
                type: 'post',
                data: new FormData(instance.form),
                cache: false,
                contentType: false,
                processData: false
            })
                .done(function (payload) {
                    if (typeof instance.options.onSuccess == 'function')
                        instance.options.onSuccess(instance.form, payload);

                    if (typeof instance.options.postSuccess == 'function')
                        instance.options.postSuccess(instance.form, payload, instance);
                })
                .fail(function (response) {
                    if (typeof instance.options.processErrors == 'function')
                        instance.options.processErrors(instance.form, response);
                    else
                        processErrors(response);
                    if (typeof instance.options.afterResponse == 'function')
                        instance.options.afterResponse(instance.form, response);
                })
        };

        var resetBtn = function () {
            $(instance.options.submitBtn).val('Submit').prop('disabled', false).removeClass('disabled');
        };

        var processErrors = function (response) {
            // we take the JSON of response and further format it for toaster
            var data = response.responseJSON;
            if (response.status == 400 && data['errors']) {
                // var errorHolder = instance.options.errorMessages[k];
                var errors = $.map(data['errors'], function (v, k) {
                    if (k == 'error_message') {
                        Materialize.toast(v, 5000, 'red accent-4');
                    } else {
                        if (k == '__all__')
                            Materialize.toast(v, 5000, 'red accent-4');
                        else {
                            var field = $(instance.form).find('[name=' + k + ']');
                            var errorHolder = instance.options.errorHolders[k];
                            var holder = field.parentsUntil(instance.options.fieldHolder).addClass('has-error');
                            if (errorHolder) {
                                holder.find(errorHolder).text(v);
                            }
                            else if (field.attr('type') == "file") {
                                field.after('<div class="help-block">' + v + '</div>');
                            }
                            else {
                                if (field.next() && field.next().hasClass('help-block')) {
                                    field.next().text(v);
                                } else {
                                    field.after('<div class="help-block ">' + v + '</div>');
                                }
                            }
                            if (k == "captcha") {
                                var field = $(instance.form).find(instance.options.captchaField);
                                $(field).addClass('has-error');
                                Materialize.toast("Captcha: " + v, 5000, 'red accent-4');
                            }
                        }
                    }
                }).join('<br>');

            } else {
                //probably server 500
                notifyServerError()
            }
            resetBtn();
        };

        instance.options.container.on('click', instance.options.submitBtn, performSubmit);

        var addFS = function (el) {
            var holder = el;
            var max = parseInt(el.find('[name*="MAX_NUM_FORMS"]').val());
            var lines = holder.find(instance.options.formSetItem).length;
            if (lines < max) {
                var fs = holder.data('item').clone();
                var num = getTotalForms(holder);  // initial id = 0, we calculate by FS items, so we will always have one more no need to increment
                // process all the fields increment numbers
                $('*', fs).each(function () {
                    var elem = $(this);
                    $.map(elem.attrs(), function (val, key) {
                        var regex = /-(\d+)-/g;
                        var match = regex.exec(val);
                        if (match) {
                            // if attribute like -num- replace the number to the next free
                            elem.attr(key, val.replace('-' + match[1] + '-', '-' + num + '-'));
                        }
                    })
                });
                fs.find('[value]').not('[type="radio"]').val('');
                fs.find('[checked]').removeAttr('checked');
                $(instance.options.formSetItem).last().after(fs);
            }
            if (lines == max - 1) {
                addButton.hide();
            }
            setTotalForms(holder);
        };

        var getTotalForms = function (holder) {
            return parseInt(holder.find('[name*="TOTAL_FORMS"]').val());
        };

        var setTotalForms = function (holder) {
            holder.find('[name*="TOTAL_FORMS"]').val($(instance.options.formSetItem).length);
        };

        var addButton = $('<button class="btn btn-default">Add</button>');
        var addNewButton = function (fs) {
            addButton.bind('click', function (e) {
                e.preventDefault();
                addFS(fs);
            })
            fs.after(addButton);
        }

        var instantiateFormSets = function () {
            if (instance.options.formSets != '') {
                $(instance.options.form_selector + ' ' + instance.options.formSets).each(function () {
                    var el = $(this);
                    el.data('item', el.find(instance.options.formSetItem).last().clone());
                    addNewButton(el);
                })
            }
        }
        instantiateFormSets();
    };

    $[pluginName] = function (options) {
        return $(options.form_selector).each(function () {
            if (!$.data(this, 'plugin_' + pluginName)) {
                $.data(this, 'plugin_' + pluginName,
                    new Plugin(this, options));
            }
        });
    }
})(jQuery, window, document);