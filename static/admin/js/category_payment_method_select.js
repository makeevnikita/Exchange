window.addEventListener('load', function() {
    django.jQuery('#id_category_payment_method').change(function(){
        var value = django.jQuery(this).val();
        if (value == 1 || value == ''){
            django.jQuery("#id_token_standart option:selected").removeAttr("selected")
            django.jQuery('#id_token_standart').css('pointer-events', 'none');
            django.jQuery("#id_token_standart option[value='1']").attr('selected', true)
        }
        if (value == 2){
            django.jQuery('#id_token_standart').css('pointer-events', 'auto');
            django.jQuery("#id_token_standart option[value='1']").attr('selected', false)
        }
    });
})