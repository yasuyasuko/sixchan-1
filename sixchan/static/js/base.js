(function () {
  const scrollAnchor = () => {
    const hiddenScrollAnchorInput = document.getElementById("scroll-anchor");
    if (hiddenScrollAnchorInput) {
      document.location.hash = hiddenScrollAnchorInput.value;
    }
  };

  const showFlashMessage = () => {
    const hiddenFlashMessages = document.getElementById("flash-messages");
    if (hiddenFlashMessages) {
      const flashMessages = hiddenFlashMessages.getElementsByTagName("div");
      for (e of flashMessages) {
        const message = e.getElementsByTagName("input")[0].value;
        const background = e.getElementsByTagName("input")[1].value;
        const options = {
          style: {
            main: {
              background: background
            }
          }
        };
        iqwerty.toast.toast(message, options);
      }
    }
  };

  // entry point
  scrollAnchor();
  showFlashMessage();
})();
