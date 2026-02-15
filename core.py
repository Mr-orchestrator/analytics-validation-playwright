from playwright.sync_api import sync_playwright, TimeoutError
import os
import json
import pandas as pd
from datetime import datetime
import pathlib
from collections import Counter
import sys
import subprocess
from pathlib import Path

def automate_tealium_add_to_cart_from_home(url):
    # Enable Playwright Inspector for live debugging
    os.environ["PWDEBUG"] = "1"
    
    with sync_playwright() as p:
        # Launch browser with Playwright UI Inspector
        browser = p.chromium.launch(
            headless=False, 
            slow_mo=1000  # Slower for better visibility in inspector
        )
        context = browser.new_context(
            viewport={'width': 1366, 'height': 768},
            record_video_dir="videos/",
            record_video_size={"width": 1366, "height": 768},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Start tracing for Playwright UI
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        
        page = context.new_page()
        
        # Storage for captured data
        captured_data = {
            'utag_data': [],
            'ga4_calls': [],
            'network_calls': []
        }
        
        # Enable console logging
        def handle_console_msg(msg):
            print(f"🖥️ Console [{msg.type}]: {msg.text}")
        
        page.on("console", handle_console_msg)
        
        # Network interception using Playwright API - Enhanced
        def handle_request(request):
            url = request.url
            # Capture all GA4 requests (including GET requests with parameters in URL)
            if 'google-analytics.com/g/collect' in url:
                print(f"🎯 GA4 Request intercepted: {request.method} {url[:100]}...")
                
                # Parse GA4 parameters from URL immediately
                try:
                    from urllib.parse import urlparse, parse_qs, unquote
                    parsed_url = urlparse(url)
                    params = parse_qs(parsed_url.query)
                    
                    # Convert to single values and decode
                    ga4_params = {}
                    for k, v in params.items():
                        if v:
                            ga4_params[k] = unquote(v[0])
                    
                    captured_data['ga4_calls'].append({
                        'url': url,
                        'params': ga4_params,
                        'method': request.method,
                        'timestamp': datetime.now().isoformat(),
                        'page': page.url
                    })
                    
                    print(f"📊 GA4 Parameters captured: {len(ga4_params)} parameters")
                    
                    # Check for purchase event
                    if ga4_params.get('en') == 'purchase':
                        print("💰 PURCHASE EVENT DETECTED!")
                        print(f"💳 Transaction ID: {ga4_params.get('ep.transaction_id', 'N/A')}")
                        print(f"💵 Value: {ga4_params.get('ep.value', 'N/A')}")
                        print(f"💰 Currency: {ga4_params.get('cu', 'N/A')}")
                        print(f"🏷️ Item ID: {ga4_params.get('ep.item_id', 'N/A')}")
                        
                except Exception as e:
                    print(f"⚠️ Error parsing GA4 URL: {str(e)}")
            
            elif 'google-analytics.com' in url or 'gtag' in url:
                print(f"🌐 Analytics Request: {request.method} {url[:80]}...")
        
        def handle_response(response):
            # We'll primarily use the request handler since GA4 data is in the URL
            pass
        
        # Enable network monitoring
        page.on("request", handle_request)
        page.on("response", handle_response)
        
        # Navigate to training URL first
        training_url = "https://ecommerce.tealiumdemo.com/training"
        print("🎓 Loading Tealium training configuration...")
        page.goto(training_url, wait_until="networkidle")
        page.wait_for_timeout(3000)
        
        # Handle Tealium Education Configuration modal
        try:
            # Wait for the modal to appear
            page.wait_for_selector(".modal-content", timeout=10000)
            print("✅ Tealium Education Configuration modal found")
            
            # Fill in the account information
            page.fill("#tu-form-account", "edu-tiq-exam-2024")
            print("✅ Account filled: edu-tiq-exam-2024")
            
            page.fill("#tu-form-profile", "exam253")
            print("✅ Profile filled: exam253")
            
            # Server and Environment should already be selected (Tealium iQ and prod)
            # Click Save changes
            page.click("#add_cookies")
            print("✅ Save changes clicked")
            page.wait_for_timeout(3000)
            
            # Now navigate to the main ecommerce site
            print("🌐 Navigating to main ecommerce site...")
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(3000)
            
        except TimeoutError:
            print("⚠️ Tealium Education Configuration modal not found, proceeding directly to site")
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(3000)
        
        # Fix viewport positioning and zoom
        page.evaluate("""
            // Reset any CSS transforms or positioning issues
            document.body.style.transform = 'none';
            document.body.style.margin = '0';
            document.body.style.padding = '0';
            document.documentElement.style.margin = '0';
            document.documentElement.style.padding = '0';
            
            // Scroll to top-left
            window.scrollTo(0, 0);
            
            console.log('🔧 Fixed viewport positioning');
        """)
        
        # Function to capture utag_data
        def capture_utag_data():
            try:
                utag_data = page.evaluate("""
                (() => {
                    const dataObj = typeof utag_data !== 'undefined' 
                        ? utag_data 
                        : (window.utag && window.utag.data ? window.utag.data : null);
                    if (dataObj) {
                        console.log('📊 utag_data found on:', window.location.pathname);
                        return {
                            url: window.location.pathname,
                            timestamp: Date.now(),
                            data: JSON.parse(JSON.stringify(dataObj))
                        };
                    }
                    return null;
                })();
                """)
                
                if utag_data:
                    captured_data['utag_data'].append(utag_data)
                    print(f"📊 utag_data captured on: {utag_data['url']}")
                    
                    # Print key purchase data if available
                    data = utag_data['data']
                    if 'order_total' in data:
                        print(f"💰 Purchase data found: Total={data.get('order_total')}, ID={data.get('order_id')}")
                        
            except Exception as e:
                print(f"⚠️ Error capturing utag_data: {str(e)}")
        
        # Initialize your exact working GA4 capture logic
        page.evaluate("""
            // Your exact working logic
            window.ga4Captured = [];
            
            // Intercept fetch calls
            const originalFetch = window.fetch;
            window.fetch = function(...args) {
                const url = args[0];
                if (url && url.includes('google-analytics.com/g/collect')) {
                    try {
                        const urlObj = new URL(url);
                        const params = Object.fromEntries(urlObj.searchParams);
                        window.ga4Captured.push({
                            url: url,
                            params: params,
                            timestamp: Date.now()
                        });
                        console.log('🎯 GA4 call captured');
                    } catch (e) {
                        console.log('Error parsing GA4 URL:', e);
                    }
                }
                return originalFetch.apply(this, args);
            };
            
            // Your exact comparison function
            window.runComparison = function() {
                console.log("🔍 Generating GA4 vs utag_data comparison table...");

                if (!window.ga4Captured || ga4Captured.length === 0) {
                    console.warn("⚠️ No GA4 calls captured. Run GA4 capture snippet first.");
                    return;
                }
                if (!window.utag || !window.utag.data) {
                    console.warn("⚠️ utag.data not found.");
                    return;
                }

                // Flatten utag_data for comparison
                const utagPurchase = {
                    order_currency: utag.data.order_currency,
                    order_total: Number(utag.data.order_total),
                    order_id: utag.data.order_id,
                    product_quantity: Number(Array.isArray(utag.data.product_quantity) ? utag.data.product_quantity[0] : utag.data.product_quantity),
                    order_tax: Number(utag.data.order_tax),
                    product_sku: Array.isArray(utag.data.product_sku) ? utag.data.product_sku[0] : utag.data.product_sku,
                };

                const ga4PurchaseCalls = ga4Captured.filter(call => call.params.en === "purchase");

                if (ga4PurchaseCalls.length === 0) {
                    console.warn("⚠️ No GA4 purchase events found.");
                    return;
                }

                ga4PurchaseCalls.forEach((call, i) => {
                    const ga4Params = {
                        item_id: call.params["ep.item_id"],
                        quantity: Number(call.params["ep.item_name"]),
                        shipping: Number(call.params["ep.shipping"]),
                        tax: Number(call.params["ep.tax"]),
                        transaction_id: call.params["ep.transaction_id"],
                        value: Number(call.params["ep.value"]),
                        currency: call.params.currency || call.params.cu
                    };

                    // Build a comparison table
                    const comparison = [
                        { parameter: "order_id / transaction_id", utag_value: utagPurchase.order_id, ga4_value: ga4Params.transaction_id, match: utagPurchase.order_id === ga4Params.transaction_id },
                        { parameter: "order_total / value", utag_value: utagPurchase.order_total, ga4_value: ga4Params.value, match: utagPurchase.order_total === ga4Params.value },
                        { parameter: "order_tax / tax", utag_value: utagPurchase.order_tax, ga4_value: ga4Params.tax, match: utagPurchase.order_tax === ga4Params.tax },
                        { parameter: "product_sku / item_id", utag_value: utagPurchase.product_sku, ga4_value: ga4Params.item_id, match: utagPurchase.product_sku === ga4Params.item_id },
                        { parameter: "product_quantity / quantity", utag_value: utagPurchase.product_quantity, ga4_value: ga4Params.quantity, match: utagPurchase.product_quantity === ga4Params.quantity },
                        { parameter: "order_currency / currency", utag_value: utagPurchase.order_currency, ga4_value: ga4Params.currency, match: utagPurchase.order_currency === ga4Params.currency },
                        { parameter: "shipping / ep.shipping", utag_value: utag.data.shipping || "N/A", ga4_value: ga4Params.shipping, match: (utag.data.shipping ? Number(utag.data.shipping) : 0) === ga4Params.shipping }
                    ];

                    console.log(`\\n📊 GA4 vs utag_data Comparison (Hit ${i + 1}):`);
                    console.table(comparison.map(row => ({
                        Parameter: row.parameter,
                        utag_data: row.utag_value,
                        GA4: row.ga4_value,
                        Match: row.match ? "✅" : "❌"
                    })));
                });
            };
            
            console.log('✅ GA4 capture initialized');
        """)
        
        print("✅ Website loaded completely and positioned correctly")
        
        # Capture initial utag_data
        capture_utag_data()
        
        # Pause for Playwright Inspector integration
        page.pause()

        # ----- 1️⃣ Handle Tealium Consent -----
        print("🍪 Checking for consent banner...")
        try:
            # Wait for consent banner and handle it
            consent_radio = page.wait_for_selector("input[type='radio'][value='optin']", timeout=5000)
            if consent_radio:
                page.check("input[type='radio'][value='optin']")
                print("✅ Opt-In selected")
                page.click("#consent_prompt_submit")
                print("✅ Consent Submit clicked")
                page.wait_for_timeout(3000)
                
                # Check cookies immediately after consent
                page.wait_for_timeout(1000)
                cookies = context.cookies()
                print(f"📋 Total cookies found: {len(cookies)}")
                
                consent_cookie = None
                for cookie in cookies:
                    if 'CONSENTMGR' in cookie['name'] or 'consent' in cookie['name'].lower():
                        consent_cookie = cookie
                        print(f"✅ Consent cookie found: {cookie['name']} = {cookie['value']}")
                        break
                
                if not consent_cookie:
                    print("⚠️ No consent cookie found after banner interaction")
            
        except TimeoutError:
            print("⚠️ Consent banner not found or timed out")
            print("🔄 Checking if site is already loaded without banner...")
            
            # Check if we can proceed without consent banner
            try:
                page.wait_for_selector("a[href*='/linen-blazer-']", timeout=3000)
                print("✅ Site appears to be loaded and ready")
            except:
                print("⚠️ Site not fully loaded, setting fallback cookie")
                context.add_cookies([{
                    'name': 'CONSENTMGR',
                    'value': 'consent:true',
                    'domain': 'ecommerce.tealiumdemo.com',
                    'path': '/',
                    'httpOnly': False,
                    'secure': False,
                    'sameSite': 'Lax'
                }])
                print("✅ Fallback cookie set")
                page.reload(wait_until="networkidle")
                page.wait_for_timeout(3000)

        # ----- 2️⃣ Click on Product Link from Home Page -----
        try:
            # Adjust selector to match the Linen Blazer link on home page
            page.wait_for_selector("a[href*='/linen-blazer-']", timeout=5000)
            page.click("a[href*='/linen-blazer-']")
            print("✅ Navigated to Linen Blazer product page")
            page.wait_for_timeout(2000)
        except TimeoutError:
            print("⚠️ Linen Blazer link not found on home page")
            return

        # ----- 3️⃣ Select Product Options & Add to Cart -----
        try:
            # Color "White"
            page.wait_for_selector("#swatch22", timeout=5000)
            page.click("#swatch22")
            print("✅ Color 'White' selected")

            # Size "XS"
            page.wait_for_selector("#swatch81", timeout=5000)
            page.click("#swatch81")
            print("✅ Size 'XS' selected")

            # Add to Cart
            page.wait_for_selector(".add-to-cart-buttons .btn-cart", timeout=5000)
            page.click(".add-to-cart-buttons .btn-cart")
            print("✅ Add to Cart clicked")
            page.wait_for_timeout(3000)
            print("✅ Product added to cart successfully")
            
            # Capture utag_data after adding to cart
            capture_utag_data()

            # Navigate to cart page first for shipping estimation
            page.goto("https://ecommerce.tealiumdemo.com/checkout/cart/")
            page.wait_for_timeout(2000)
            print("✅ Navigated to cart page")
            
            # Capture utag_data on cart page
            capture_utag_data()

            # Step 1: Select India
            page.evaluate("""
                console.log('🇮🇳 Setting country to India...');
                document.getElementById('country').value = 'IN';
                document.getElementById('country').dispatchEvent(new Event('change', { bubbles: true }));
                console.log('✅ Country set to India');
            """)

            # Step 2: Set Tamil Nadu (wait for country to load first)
            page.wait_for_timeout(1000)
            page.evaluate("""
                console.log('🏛️ Setting region to Tamil Nadu...');
                document.getElementById('region').value = 'Tamil Nadu';
                document.getElementById('region').style.display = 'block';
                console.log('✅ Region set to Tamil Nadu');
            """)

            # Step 3: Set zip code
            page.evaluate("""
                console.log('📮 Setting zip code...');
                document.getElementById('postcode').value = '641035';
                console.log('✅ Zip code set to 641035');
            """)

            # Step 4: Click Estimate
            page.evaluate("""
                console.log('💰 Clicking estimate button...');
                document.querySelector('button[onclick="coShippingMethodForm.submit()"]').click();
                console.log('✅ Estimate button clicked');
            """)
            page.wait_for_timeout(2000)

            # Select the Free Shipping radio button
            page.evaluate("""
                console.log('🚚 Selecting free shipping...');
                document.getElementById('s_method_freeshipping_freeshipping').checked = true;
                console.log('✅ Free shipping selected');
            """)

            # Click the Update Total button
            page.evaluate("""
                console.log('🔄 Updating total...');
                document.querySelector('button[name="do"][value="Update Total"]').click();
                console.log('✅ Total updated');
            """)
            page.wait_for_timeout(2000)

            # Step 7: Proceed to Checkout
            page.evaluate("""
                console.log('🛒 Proceeding to checkout...');
                document.querySelector('.btn-proceed-checkout').click();
                console.log('✅ Proceeding to checkout');
            """)
            print("✅ Shipping estimation completed and proceeding to checkout")
            page.wait_for_timeout(3000)

            # Now continue with checkout process
            page.wait_for_timeout(2000)
            print("✅ Navigated to checkout page")

            # Step 1: Select Guest Checkout
            page.evaluate("""
                console.log('👤 Selecting guest checkout...');
                document.getElementById('login:guest').checked = true;
                document.getElementById('onepage-guest-register-button').click();
                console.log('✅ Guest checkout selected');
            """)
            print("✅ Guest checkout selected")
            page.wait_for_timeout(2000)

            # Step 2: Fill Billing Information
            page.evaluate("""
                console.log('📝 Filling billing information...');
                document.getElementById('billing:firstname').value = 'John';
                document.getElementById('billing:lastname').value = 'Doe';
                document.getElementById('billing:email').value = 'john.doe@example.com';
                document.getElementById('billing:street1').value = '123 Main Street';
                document.getElementById('billing:city').value = 'Chennai';
                document.getElementById('billing:postcode').value = '641035';
                document.getElementById('billing:telephone').value = '9876543210';
                console.log('✅ Basic billing info filled');
            """)
            
            # Set country to India
            page.evaluate("""
                console.log('🇮🇳 Setting billing country to India...');
                document.getElementById('billing:country_id').value = 'IN';
                document.getElementById('billing:country_id').dispatchEvent(new Event('change'));
                console.log('✅ Billing country set to India');
            """)
            print("✅ Billing information filled")
            page.wait_for_timeout(2000)

            # Set region to Tamil Nadu and continue billing
            page.evaluate("""
                console.log('🏛️ Setting billing region and continuing...');
                document.getElementById('billing:region').value = 'Tamil Nadu';
                document.querySelector('#billing-buttons-container .button').click();
                console.log('✅ Billing completed and continued');
            """)
            print("✅ Billing continue clicked")
            page.wait_for_timeout(3000)

            # Step 3: Use same billing address for shipping
            page.evaluate("""
                console.log('🏠 Using same address for shipping...');
                document.getElementById('shipping:same_as_billing').checked = true;
                document.getElementById('shipping:same_as_billing').dispatchEvent(new Event('change'));
                document.querySelector('#shipping-buttons-container .button').click();
                console.log('✅ Shipping address set and continued');
            """)
            print("✅ Shipping continue clicked")
            page.wait_for_timeout(3000)

            # Step 4: Select Free Shipping
            page.evaluate("""
                console.log('🚚 Selecting shipping method...');
                document.querySelector('input[value*="freeshipping"]').checked = true;
                document.querySelector('input[value*="freeshipping"]').dispatchEvent(new Event('change'));
                document.querySelector('#shipping-method-buttons-container .button').click();
                console.log('✅ Free shipping method selected and continued');
            """)
            print("✅ Free shipping selected and continued")
            page.wait_for_timeout(3000)

            # Step 5: Continue with Payment (default payment method)
            page.evaluate("""
                console.log('💳 Proceeding with payment...');
                document.querySelector('#payment-buttons-container .button').click();
                console.log('✅ Payment method confirmed');
            """)
            print("✅ Payment continue clicked")
            page.wait_for_timeout(3000)

            # Step 6: Place Order
            page.evaluate("""
                console.log('🎯 Placing final order...');
                document.querySelector('button[onclick="review.save();"]').click();
                console.log('🎉 ORDER PLACED SUCCESSFULLY!');
            """)
            print("✅ Order placed successfully!")
            page.wait_for_timeout(3000)
            
            # Wait for success page to be ready and utag to load
            print("🎉 Waiting for success page to be ready...")
            
            # Check if we're on success page
            try:
                page.wait_for_url("**/success/**", timeout=10000)
                print("✅ Success page URL confirmed")
            except:
                print("⚠️ Success page URL not detected, continuing...")
            
            # Wait for page to be fully loaded (no active requests)
            page.wait_for_load_state("networkidle", timeout=15000)
            print("✅ Network idle - page fully loaded")
            
            # 🎯 CHECK LOADED GA4 CALLS (Your main request)
            print("🔍 Checking GA4 calls already loaded in browser...")
            
            ga4_calls = page.evaluate("""
            (() => {
              const entries = performance.getEntriesByType("resource")
                .filter(e => e.name.includes("google-analytics.com/g/collect"))
                .map(e => {
                  const query = e.name.split("?")[1] || "";
                  const params = Object.fromEntries(new URLSearchParams(query));
                  return { url: e.name, params };
                });

              console.log(`✅ Found ${entries.length} GA4 call(s) from Performance API`);
              entries.forEach((c, i) => {
                console.log(`--- GA4 Hit ${i + 1} ---`);
                console.table(c.params);
              });
              return entries;
            })();
            """)

            if not ga4_calls:
                print("⚠️ No GA4 calls found in loaded resources.")
            else:
                print(f"✅ {len(ga4_calls)} GA4 call(s) captured from Performance API.")
                for i, call in enumerate(ga4_calls):
                    event_name = call['params'].get('en', 'N/A')
                    transaction_id = call['params'].get('ep.transaction_id', 'N/A')
                    value = call['params'].get('ep.value', 'N/A')
                    print(f"Hit {i+1}: event={event_name}  transaction_id={transaction_id}  value={value}")
                    
                    # Store in captured_data for later analysis
                    captured_data['ga4_calls'].append({
                        'url': call['url'],
                        'params': call['params'],
                        'method': 'GET',
                        'timestamp': datetime.now().isoformat(),
                        'page': page.url,
                        'source': 'Performance API - Main Check'
                    })
            
            # 🔍 CAPTURE ALL COMPLETED NETWORK REQUESTS using Performance API
            print("🔍 Extracting all completed network requests from Performance API...")
            
            all_requests = page.evaluate("""
            (() => {
              const entries = performance.getEntriesByType("resource");
              if (!entries || entries.length === 0) {
                console.warn("⚠️ No resource entries found in Performance API");
                return [];
              }

              return entries.map(e => {
                const url = e.name;
                const paramsObj = {};
                try {
                  const query = url.split("?")[1];
                  if (query) {
                    for (const [k, v] of new URLSearchParams(query)) {
                      paramsObj[k] = v;
                    }
                  }
                } catch (err) {
                  console.warn("Error parsing params for", url, err);
                }

                // Identify request type for easy filtering later
                let category = "Other";
                if (url.includes("google-analytics.com/g/collect")) category = "GA4";
                else if (url.includes("doubleclick.net")) category = "Floodlight";
                else if (url.includes("adservice.google.com")) category = "Google Ads";
                else if (url.includes("omtrdc.net") || url.includes("2o7.net")) category = "Adobe Analytics";
                else if (url.includes("tealiumiq.com") || url.includes("tealium.com")) category = "Tealium";
                else if (url.includes("gtm.js") || url.includes("googletagmanager.com")) category = "GTM";
                else if (url.includes("facebook.com/tr")) category = "Facebook Pixel";
                else if (url.includes("bat.bing.com")) category = "Bing Ads";
                else if (url.includes("pinterest.com/v3/")) category = "Pinterest";
                else if (url.includes("snapchat.com/p")) category = "Snapchat";
                else if (url.includes("tiktok.com/i/")) category = "TikTok";

                return {
                  name: e.name,
                  type: e.initiatorType,
                  duration: e.duration ? e.duration.toFixed(2) : "0",
                  size: e.transferSize || 0,
                  category,
                  params: paramsObj
                };
              });
            })();
            """)
            
            if not all_requests:
                print("⚠️ No network requests found in Performance API.")
            else:
                print(f"✅ Found {len(all_requests)} network requests via Performance API")

                # Filter and display categorized counts
                categories = [r['category'] for r in all_requests]
                summary = Counter(categories)
                print("📊 Request Categories Summary:")
                for k, v in summary.items():
                    print(f"   {k:<20}: {v}")

                # Save all requests to Excel for debugging
                now = datetime.now()
                folder = pathlib.Path(f"validation_results/{now.strftime('%Y-%m-%d')}")
                folder.mkdir(parents=True, exist_ok=True)
                file_path = folder / f"All_Network_Requests_{now.strftime('%H-%M-%S')}.xlsx"

                df = pd.DataFrame(all_requests)
                df.to_excel(file_path, index=False)
                print(f"📁 Exported all network requests to: {file_path}")
                
                # Store in captured_data for later analysis
                captured_data['network_calls'] = all_requests
                
                # Show detailed breakdown of tracking requests
                tracking_requests = [r for r in all_requests if r['category'] != 'Other']
                if tracking_requests:
                    print(f"\n🎯 Found {len(tracking_requests)} tracking/analytics requests:")
                    for req in tracking_requests:
                        print(f"   📡 {req['category']}: {req['name'][:80]}...")
                        if req['category'] == 'GA4' and req['params']:
                            event_name = req['params'].get('en', 'N/A')
                            transaction_id = req['params'].get('ep.transaction_id', 'N/A')
                            print(f"      └─ Event: {event_name}, Transaction: {transaction_id}")
                
                # Capture GA4 hits using Performance API (handles both GET and POST)
                ga4_results = page.evaluate("""
                (() => {
                  const entries = performance.getEntriesByType("resource");
                  const ga4Calls = entries
                    .filter(e => e.name.includes("google-analytics.com/g/collect"))
                    .map(e => {
                      let params = {};
                      try {
                        // For GET requests, params are in URL
                        const queryString = e.name.split("?")[1];
                        if (queryString) {
                          params = Object.fromEntries(new URLSearchParams(queryString));
                        }
                        // For POST requests, we can't get body params from Performance API
                        // but we can still identify the request
                        return { 
                          url: e.name, 
                          params: params,
                          method: e.name.includes("?") ? "GET" : "POST",
                          duration: e.duration,
                          size: e.transferSize
                        };
                      } catch (err) {
                        console.warn("Error parsing GA4 request:", err);
                        return { url: e.name, params: {}, method: "UNKNOWN" };
                      }
                    });
                  
                  console.log(`✅ Found ${ga4Calls.length} GA4 call(s) via Performance API`);
                  ga4Calls.forEach((call, i) => {
                    console.log(`--- GA4 Hit ${i + 1} (${call.method}) ---`);
                    console.log("URL:", call.url.substring(0, 100) + "...");
                    if (Object.keys(call.params).length > 0) {
                      console.table(call.params);
                    } else {
                      console.log("(POST request - parameters in body, captured by request interceptor)");
                    }
                  });
                  return ga4Calls;
                })();
                """)

                if ga4_results:
                    print(f"✅ Found {len(ga4_results)} GA4 call(s) via Performance API")
                    for i, call in enumerate(ga4_results):
                        event_name = call['params'].get('en', 'N/A')
                        transaction_id = call['params'].get('ep.transaction_id', 'N/A')
                        print(f"GA4 Hit {i+1}: en={event_name} transaction_id={transaction_id}")
                    
                    # Combine with existing GA4 captures to avoid duplicates
                    existing_urls = {call['url'] for call in captured_data['ga4_calls']}
                    for ga4_call in ga4_results:
                        if ga4_call['url'] not in existing_urls:
                            captured_data['ga4_calls'].append({
                                'url': ga4_call['url'],
                                'params': ga4_call['params'],
                                'method': 'GET',
                                'timestamp': datetime.now().isoformat(),
                                'page': page.url,
                                'source': 'Performance API'
                            })
                else:
                    print("⚠️ No GA4 calls found using Performance API.")
            
            # Check if utag is loaded and ready
            utag_ready = False
            for attempt in range(10):  # Try for 10 seconds
                try:
                    utag_status = page.evaluate("""
                    (() => {
                        // Check if utag is loaded
                        if (typeof utag !== 'undefined' && utag.data) {
                            return {
                                loaded: true,
                                hasData: Object.keys(utag.data).length > 0,
                                dataKeys: Object.keys(utag.data).length
                            };
                        }
                        return { loaded: false, hasData: false, dataKeys: 0 };
                    })();
                    """)
                    
                    if utag_status['loaded'] and utag_status['hasData']:
                        print(f"✅ utag loaded with {utag_status['dataKeys']} data fields")
                        utag_ready = True
                        break
                    else:
                        print(f"⏳ Waiting for utag... (attempt {attempt + 1}/10)")
                        page.wait_for_timeout(1000)
                        
                except Exception as e:
                    print(f"⏳ Checking utag status... (attempt {attempt + 1}/10)")
                    page.wait_for_timeout(1000)
            
            if not utag_ready:
                print("⚠️ utag not fully loaded, but continuing...")
            
            # Additional wait to ensure all tracking calls are sent
            print("⏳ Waiting for tracking calls to complete...")
            page.wait_for_timeout(3000)
            
            # Skip the browser-side validation since we have better Python-side validation
            print("🔍 Using Python-side validation with captured data...")
            
            # Check if we have GA4 calls captured
            if not captured_data['ga4_calls']:
                print("❌ No GA4 calls found in captured_data")
                print("🔍 Let's check what we captured:")
                print(f"   - Total network requests: {len(captured_data.get('network_calls', []))}")
                print(f"   - GA4 calls: {len(captured_data['ga4_calls'])}")
                print(f"   - utag_data captures: {len(captured_data['utag_data'])}")
            else:
                print(f"✅ Found {len(captured_data['ga4_calls'])} GA4 calls in captured data")
                
                # Show details of captured GA4 calls
                for i, call in enumerate(captured_data['ga4_calls']):
                    event_name = call['params'].get('en', 'N/A')
                    transaction_id = call['params'].get('ep.transaction_id', 'N/A')
                    print(f"   GA4 Call {i+1}: Event={event_name}, Transaction={transaction_id}")
            
            # Get utag_data from the page for validation
            utag_data_result = page.evaluate("""
                // Get utag_data from the page
                (function() {
                    if (typeof utag_data !== 'undefined') {
                        return { success: true, data: utag_data };
                    } else if (typeof utag !== 'undefined' && utag.data) {
                        return { success: true, data: utag.data };
                    } else {
                        return { success: false, error: "utag_data not found" };
                    }
                })();
            """)
            
            if utag_data_result and utag_data_result.get('success'):
                print("✅ utag_data found on page")
                utag_data = utag_data_result['data']
                
                # Show utag_data details
                if utag_data.get('order_total'):
                    print(f"   Order Total: {utag_data.get('order_total')}")
                    print(f"   Order ID: {utag_data.get('order_id')}")
                    print(f"   Product SKU: {utag_data.get('product_sku')}")
                else:
                    print("⚠️ No purchase data found in utag_data")
            else:
                print(f"❌ utag_data not found: {utag_data_result.get('error', 'Unknown error')}")
            
            # Capture final utag_data on success page
            capture_utag_data()
            
            # Perform validation using captured data (after process completion)
            try:
                print("\n" + "="*50)
                print("📊 GA4 vs utag_data COMPARISON TABLE")
                print("="*50)
                
                # Find latest utag_data with purchase info
                utag_purchase = None
                print("🔍 Looking for utag_data with purchase info...")
                for utag in reversed(captured_data['utag_data']):
                    if 'order_total' in utag['data'] and utag['data'].get('order_total'):
                        utag_purchase = utag['data']
                        print(f"✅ Found purchase utag_data on: {utag['url']}")
                        break
                
                if not utag_purchase:
                    print("❌ No utag_data with purchase info found")
                    browser.close()
                    return
                
                # Flatten utag_data for comparison
                utag_flattened = {
                    'order_currency': utag_purchase.get('order_currency'),
                    'order_total': float(utag_purchase.get('order_total', 0)) if utag_purchase.get('order_total') else 0,
                    'order_id': utag_purchase.get('order_id'),
                    'product_quantity': float(utag_purchase.get('product_quantity', [0])[0] if isinstance(utag_purchase.get('product_quantity'), list) else utag_purchase.get('product_quantity', 0)) if utag_purchase.get('product_quantity') else 0,
                    'order_tax': float(utag_purchase.get('order_tax', 0)) if utag_purchase.get('order_tax') else 0,
                    'product_sku': utag_purchase.get('product_sku', [None])[0] if isinstance(utag_purchase.get('product_sku'), list) else utag_purchase.get('product_sku'),
                    'shipping': float(utag_purchase.get('shipping', 0)) if utag_purchase.get('shipping') else 0
                }
                
                # Find GA4 purchase calls
                ga4_purchase_calls = [call for call in captured_data['ga4_calls'] if call['params'].get('en') == 'purchase']
                
                if not ga4_purchase_calls:
                    print("⚠️ No GA4 purchase events found.")
                    browser.close()
                    return
                
                # Build comparison for each GA4 purchase call
                for call_idx, call in enumerate(ga4_purchase_calls):
                    ga4_params = {
                        'item_id': call['params'].get('ep.item_id'),
                        'quantity': float(call['params'].get('ep.item_name', 0)) if call['params'].get('ep.item_name') else 0,
                        'shipping': float(call['params'].get('ep.shipping', 0)) if call['params'].get('ep.shipping') else 0,
                        'tax': float(call['params'].get('ep.tax', 0)) if call['params'].get('ep.tax') else 0,
                        'transaction_id': call['params'].get('ep.transaction_id'),
                        'value': float(call['params'].get('ep.value', 0)) if call['params'].get('ep.value') else 0,
                        'currency': call['params'].get('currency') or call['params'].get('cu')
                    }
                    
                    # Build comparison table
                    comparison = [
                        {
                            'parameter': 'order_id / transaction_id',
                            'utag_value': str(utag_flattened['order_id']),
                            'ga4_value': str(ga4_params['transaction_id']),
                            'match': str(utag_flattened['order_id']) == str(ga4_params['transaction_id'])
                        },
                        {
                            'parameter': 'order_total / value',
                            'utag_value': str(utag_flattened['order_total']),
                            'ga4_value': str(ga4_params['value']),
                            'match': utag_flattened['order_total'] == ga4_params['value']
                        },
                        {
                            'parameter': 'order_tax / tax',
                            'utag_value': str(utag_flattened['order_tax']),
                            'ga4_value': str(ga4_params['tax']),
                            'match': utag_flattened['order_tax'] == ga4_params['tax']
                        },
                        {
                            'parameter': 'product_sku / item_id',
                            'utag_value': str(utag_flattened['product_sku']),
                            'ga4_value': str(ga4_params['item_id']),
                            'match': str(utag_flattened['product_sku']) == str(ga4_params['item_id'])
                        },
                        {
                            'parameter': 'product_quantity / quantity',
                            'utag_value': str(utag_flattened['product_quantity']),
                            'ga4_value': str(ga4_params['quantity']),
                            'match': utag_flattened['product_quantity'] == ga4_params['quantity']
                        },
                        {
                            'parameter': 'order_currency / currency',
                            'utag_value': str(utag_flattened['order_currency']),
                            'ga4_value': str(ga4_params['currency']),
                            'match': str(utag_flattened['order_currency']) == str(ga4_params['currency'])
                        },
                        {
                            'parameter': 'shipping / ep.shipping',
                            'utag_value': str(utag_flattened['shipping']),
                            'ga4_value': str(ga4_params['shipping']),
                            'match': utag_flattened['shipping'] == ga4_params['shipping']
                        }
                    ]
                    
                    print(f"\n📊 GA4 vs utag_data Comparison (Hit {call_idx + 1}):")
                    print("-" * 80)
                    for row in comparison:
                        match_symbol = "✅" if row['match'] else "❌"
                        print(f"{row['parameter']:<30} | utag: {row['utag_value']:<15} | GA4: {row['ga4_value']:<15} | {match_symbol}")
                    
                    # Summary
                    matches = sum(1 for row in comparison if row['match'])
                    total = len(comparison)
                    print(f"\n📈 Match Rate: {matches}/{total} ({(matches/total*100):.1f}%)")
                    
                    # Export to runtime_data for dashboard
                    runtime_file = Path("runtime_data/last_run.json")
                    runtime_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Get current timestamp for this test run
                    test_timestamp = datetime.now()
                    
                    export_data = []
                    for row_idx, row in enumerate(comparison):
                        export_data.append({
                            'Date': test_timestamp.strftime("%Y-%m-%d"),
                            'Time': test_timestamp.strftime("%H:%M"),
                            'Timestamp': test_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                            'Hit': call_idx + 1,
                            'Test Case': row['parameter'],
                            'Result': 'Pass' if row['match'] else 'Fail',
                            'Expected': row['utag_value'],
                            'Actual': row['ga4_value'],
                            'parameter': row['parameter'],
                            'utag_value': row['utag_value'],
                            'ga4_value': row['ga4_value'],
                            'match': row['match'],
                            'hit_number': call_idx + 1
                        })
                    
                    with open(runtime_file, 'w') as f:
                        json.dump(export_data, f, indent=2)
                    print(f"\n📁 Dashboard data exported to: {runtime_file}")
                    print(f"⏰ Test executed at: {test_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                
                print("\n" + "="*50)
                print("📋 Capture Summary:")
                print(f"   - utag_data captures: {len(captured_data['utag_data'])}")
                print(f"   - GA4 calls: {len(captured_data['ga4_calls'])}")
                print(f"   - GA4 purchase events: {len(ga4_purchase_calls)}")
                print(f"   - Total network requests: {len(captured_data.get('network_calls', []))}")
                print("="*50)
                
            except Exception as e:
                print(f"⚠️ Error performing validation: {str(e)}")
                import traceback
                traceback.print_exc()
        
        except Exception as e:
            print(f"⚠️ Error in checkout process: {str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            try:
                # Get video path before closing the page
                video_path = None
                try:
                    video_path = page.video.path()
                    print(f"📹 Video recorded at: {video_path}")
                except Exception as e:
                    print(f"⚠️ Could not get video path: {str(e)}")
                
                # Close page to finalize video
                page.close()
                
                # Rename video with meaningful name
                if video_path and os.path.exists(video_path):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    video_dir = Path("videos")
                    video_dir.mkdir(exist_ok=True)
                    new_video_name = f"test_run_{timestamp}.webm"
                    new_video_path = video_dir / new_video_name
                    
                    try:
                        import shutil
                        shutil.move(video_path, new_video_path)
                        print(f"✅ Video saved as: {new_video_path}")
                    except Exception as e:
                        print(f"⚠️ Could not rename video: {str(e)}")
                
                # Prepare output directory and timestamp
                output_dir = Path("validation_results")
                output_dir.mkdir(exist_ok=True)
                
                # Generate timestamp for file naming (with minutes)
                file_timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                
                # Save Playwright trace to validation_results with timestamp
                trace_filename = f"playwright_trace_{file_timestamp}.zip"
                trace_path = output_dir / trace_filename
                context.tracing.stop(path=str(trace_path))
                print(f"✅ Playwright trace saved to: {trace_path.absolute()}")
                
                # Save data to Excel with timestamped names
                if captured_data.get('ga4_calls') or captured_data.get('utag_data'):
                    
                    # Save GA4 calls to Excel
                    if captured_data.get('ga4_calls'):
                        ga4_df = pd.json_normalize(captured_data['ga4_calls'])
                        ga4_excel_path = output_dir / f"ga4_calls_{file_timestamp}.xlsx"
                        ga4_df.to_excel(ga4_excel_path, index=False)
                        print(f"✅ GA4 calls saved to: {ga4_excel_path}")
                    
                    # Save utag data to Excel
                    if captured_data.get('utag_data'):
                        utag_df = pd.json_normalize(captured_data['utag_data'])
                        utag_excel_path = output_dir / f"utag_data_{file_timestamp}.xlsx"
                        utag_df.to_excel(utag_excel_path, index=False)
                        print(f"✅ utag data saved to: {utag_excel_path}")
                    
                    # Save comparison results to Excel if they exist
                    if 'comparison' in locals():
                        comp_df = pd.DataFrame(comparison)
                        comp_excel_path = output_dir / f"ga4_vs_utag_comparison_{file_timestamp}.xlsx"
                        comp_df.to_excel(comp_excel_path, index=False)
                        print(f"✅ Comparison results saved to: {comp_excel_path}")
                        
            except Exception as e:
                print(f"⚠️ Error while saving files: {str(e)}")
            
            finally:
                browser.close()
                print("✅ Browser closed")

if __name__ == "__main__":
    url = "https://ecommerce.tealiumdemo.com/"
    automate_tealium_add_to_cart_from_home(url)
    
    # Auto-launch dashboard after test completion
    print("\n" + "="*80)
    print("🚀 Test completed! Launching dashboard...")
    print("="*80 + "\n")
    
    try:
        import webbrowser
        import time
        
        # Start dashboard in background
        dashboard_process = subprocess.Popen(
            [sys.executable, "dashboard.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for dashboard to start
        time.sleep(3)
        
        # Open browser
        webbrowser.open("http://127.0.0.1:8050/")
        print("✅ Dashboard opened in browser at http://127.0.0.1:8050/")
        print("Press Ctrl+C to stop the dashboard")
        
        # Keep dashboard running
        dashboard_process.wait()
        
    except KeyboardInterrupt:
        print("\n⚠️ Dashboard stopped by user")
        if 'dashboard_process' in locals():
            dashboard_process.terminate()
    except Exception as e:
        print(f"⚠️ Could not auto-launch dashboard: {str(e)}")
        print("You can manually run: python dashboard.py")
