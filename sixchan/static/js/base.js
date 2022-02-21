(function () {
    const scrollAnchor = () => {
        const hiddenScrollAnchorInput = document.getElementById('scroll-anchor')
        if (hiddenScrollAnchorInput) {
            document.location.hash = hiddenScrollAnchorInput.value
        }
    }

    const showFlashMessage = () => {
        const hiddenFlashMessages = document.getElementById('flash-messages')
        if (hiddenFlashMessages) {
            const flashMessages = hiddenFlashMessages.getElementsByTagName('div')
            flashMessages.forEach(e => {
                const message = e.getElementsByName('message')[0].value
                const background = e.getElementsByName('background')[0].value
                const options = {
                    style: { main: { background: background } }
                }
                iqwerty.toast.toast(message, options)
            });
        }
    }

    // entry point
    scrollAnchor()
    showFlashMessage()
}())