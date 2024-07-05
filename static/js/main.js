console.log("Sanity check!");

// Get Stripe publishable key
fetch("/config/")
  .then((result) => {
    if (!result.ok) {
      throw new Error("Failed to fetch Stripe config");
    }
    return result.json();
  })
  .then((data) => {
    // Initialize Stripe.js
    const stripe = Stripe(data.publicKey);
    // Event handler
    const planStartupBtn = document.getElementsByClassName("get-started-btn");
    if (planStartupBtn.length) {
      for (let index = 0; index < planStartupBtn.length; index++) {
        const ele = planStartupBtn[index];
        ele.addEventListener("click", (event) => {
          // Get Checkout Session ID
          const planPrice = parseFloat(event.target.value);
          const planName = event.target.ariaLabel.split(";")[0];
          const planDesc = event.target.ariaLabel.split(";")[1];
          fetch("/create-checkout-session/", {
            method: "POST",
            body: JSON.stringify({
              planDesc,
              planName,
              planPrice
            }),
            headers: {
              "Content-Type": "application/json"
            }
          })
            .then((result) => {
              if (!result.ok) {
                throw new Error("Failed to create checkout session");
              }
              return result.json();
            })
            .then((data) => {
              // Redirect to Stripe Checkout
              return stripe.redirectToCheckout({ sessionId: data.sessionId });
            })
            .catch((error) => {
              console.error("Error during checkout process:", error);
            });
        });
      }
    }
  })
  .catch((error) => {
    console.error("Error fetching Stripe config:", error);
  });
