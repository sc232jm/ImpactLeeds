const im = iframemanager();

im.run({
    onChange: ({changedServices, eventSource}) => {
        if (eventSource.type === 'click') {
            const servicesToAccept = [
                ...CookieConsent.getUserPreferences().acceptedServices['analytics'],
                ...changedServices,
            ];

            CookieConsent.acceptService(servicesToAccept, 'analytics');
        }
    },

    currLang: 'en',

});

CookieConsent.run({
    guiOptions: {
        consentModal: {
            layout: 'box inline',
            position: 'bottom left',
            equalWeightButtons: true,
            flipButtons: false,
        },
        preferencesModal: {
            layout: 'box',
            equalWeightButtons: true,
            flipButtons: false,
        },
    },

    categories: {
        necessary: {
            readOnly: true,
            enabled: true,
        },

        analytics: {},
    },

    language: {
        default: 'en',

        translations: {
            en: '/static/js/en.json',
        },
    },
});
