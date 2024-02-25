listeners = """
if (!window.hasInjected) {
    window.recordedEvents = [];
    window.hasInjected = true;
    window.isPaused = false;
    window.isDropdown = false;

    console.log("Listeners have been set up");
    function sendEventsToServerSync() {
        console.log("Sending the respective event to the server");
        if (window.isSending || window.recordedEvents.length === 0) {
            return; // Do not send if a send operation is in progress or if there are no events to send
        }
        window.isSending = true;

        var xhr = new XMLHttpRequest();
        xhr.open("POST", 'http://localhost:9005/save', true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState == 4) {
                if (xhr.status == 200) {
                    console.log('Event data sent successfully');
                }
                window.isSending = false;
                window.recordedEvents = []; // Clear the recorded events after sending
            }
        };

        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify(window.recordedEvents));
    }

    function backspaceServerSync(xpath) {
        console.log("Sending the backspace event to the server");
        if (window.isSending || xpath.length === 0) {
            return; // Do not send if a send operation is in progress or if there are no events to send
        }
        window.isSending = true;

        var xhr = new XMLHttpRequest();
        xhr.open("POST", 'http://localhost:9005/delete-backspace', true);
        xhr.onreadystatechange = function() {
            if (xhr.readyState == 4) {
                if (xhr.status == 200) {
                    console.log('Event data sent successfully');
                }
                window.isSending = false;
                window.recordedEvents = []; // Clear the recorded events after sending
            }
        };

        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify({ xpath: xpath }));
    }

    var clickTimer;
    var doubleClickFlag = false;

    function getFrameInfo() {
        if (window !== window.top) {
            return {
                isInFrame: true,
                frameId: window.frameElement ? window.frameElement.id : 'unknownFrame'
            };
        } else {
            return {
                isInFrame: false,
                frameId: null
            };
        }
    }

    function isInIframe() {
        return window !== window.top;
    }
    function setFrameDetected(value) {
        localStorage.setItem('frameDetected', value.toString());
    }
    function getFrameDetected() {
        return localStorage.getItem('frameDetected') === 'true';
    }

    window.frameDetected = getFrameDetected();


    document.addEventListener('dblclick', function(e) {
        console.log("Double Click ...");
        if (window.isPaused) return;
        doubleClickFlag = true;
        clearTimeout(clickTimer);
        var xpath = computeXPath(e.target);
        var frameInfo = getFrameInfo(e.target);
        console.log(frameInfo);
        var currentFrameDetected = getFrameDetected(); // Get the current state from localStorage
        console.log(currentFrameDetected);
        if (frameInfo.frameId !== null && !currentFrameDetected){
            window.frameDetected = true;
            console.log('Detected a frame for clicked element');
            console.log(frameInfo.frameId);
            setFrameDetected(true);
            window.recordedEvents.push(['frame', Date.now(), frameInfo.frameId]);
        } else if (frameInfo.frameId === null && currentFrameDetected){
            window.frameDetected = false;
            console.log('You have now left the frame to the parent body');
            setFrameDetected(false);
            window.recordedEvents.push(['frame', Date.now(), 'parent']);
        }
        window.recordedEvents.push(['dblClick', Date.now(), xpath]);
        sendEventsToServerSync();
        doubleClickFlag = false;
    });
    
    document.addEventListener('click', function(e) {
        if (window.isPaused) return;
        if (!doubleClickFlag) {
            clearTimeout(clickTimer);
            clickTimer = setTimeout(function() {
                if (!doubleClickFlag) {
                    console.log("You clicked right now ...");
                    var xpath = computeXPath(e.target);
                    var frameInfo = getFrameInfo(e.target);
                    console.log(frameInfo);
                    var currentFrameDetected = getFrameDetected(); // Get the current state from localStorage
                    console.log(currentFrameDetected);
                    if (frameInfo.frameId !== null && !currentFrameDetected){
                        window.frameDetected = true;
                        console.log('Detected a frame for clicked element');
                        console.log(frameInfo.frameId);
                        setFrameDetected(true);
                        window.recordedEvents.push(['frame', Date.now(), frameInfo.frameId]);
                    } else if (frameInfo.frameId === null && currentFrameDetected){
                        window.frameDetected = false;
                        console.log('You have now left the frame to the parent body');
                        setFrameDetected(false);
                        window.recordedEvents.push(['frame', Date.now(), 'parent']);
                    }
                    if (!(xpath.includes('//select')) && !window.isDropdown){
                        window.recordedEvents.push(['click', Date.now(), xpath]);
                        }
                    else if (!window.isDropdown){
                        window.recordedEvents.push(['dropdownXpath', Date.now(), xpath]);
                        window.isDropdown = true;
                    }
                    else{
                           console.log("Dropdown detected");
                           window.isDropdown = false;
                           var selectedOptionText = e.target.options[e.target.selectedIndex].text; 
                           window.recordedEvents.push(['dropdownText', Date.now(), selectedOptionText]);
                    }    
                    sendEventsToServerSync();
                }
                doubleClickFlag = false;
            }, 300); // Adjust the timeout duration (300ms) as needed
        }
    });

    let ctrlAPressedAndReleased = false;

    document.addEventListener('keydown', function(e) {
        if (window.isPaused) return;
        var xpath = computeXPath(e.target);
        var frameInfo = getFrameInfo(e.target);
        console.log(frameInfo);
        var currentFrameDetected = getFrameDetected(); // Get the current state from localStorage
        console.log(currentFrameDetected);
        if (frameInfo.frameId !== null && !currentFrameDetected){
            window.frameDetected = true;
            console.log('Detected a frame for clicked element');
            console.log(frameInfo.frameId);
            setFrameDetected(true);
            window.recordedEvents.push(['frame', Date.now(), frameInfo.frameId]);
        } else if (frameInfo.frameId === null && currentFrameDetected){
            window.frameDetected = false;
            console.log('You have now left the frame to the parent body');
            setFrameDetected(false);
            window.recordedEvents.push(['frame', Date.now(), 'parent']);
        }
        console.log(e.key);
        if (e.ctrlKey && e.key === 'a') {
            ctrlAPressedAndReleased = true;
        } else if (ctrlAPressedAndReleased && e.key === 'Backspace') {
            window.recordedEvents.push(['clearinput', Date.now(), xpath]);
            sendEventsToServerSync();
            ctrlAPressedAndReleased = false;
        }
        else if (e.key.length === 1){
            window.recordedEvents.push(['input', Date.now(), xpath, e.key]);
            sendEventsToServerSync();
            }
        else if (e.key === 'Backspace'){
            console.log('Getting ready to backspace');
            backspaceServerSync(xpath);
        }
        else if (e.key === 'Enter'){
            window.recordedEvents.push(['specialKeys', Date.now(), xpath, e.key]);
            sendEventsToServerSync();
        }  
    });

    function recordPageLoadEvent() {
        if (window.recordedEvents.length === 0 || window.recordedEvents[window.recordedEvents.length - 1][0] !== 'WaitForPageLoad') {
            window.recordedEvents.push(['WaitForPageLoad', Date.now()]);
            sendEventsToServerSync();  
        }
    }

    document.addEventListener('scroll', function(e) {
        if (window.isPaused) return;
        var xpath = computeXPathOfElementAt20Percent()
        var frameInfo = getFrameInfo(e.target);
        console.log(frameInfo);
        var currentFrameDetected = getFrameDetected(); // Get the current state from localStorage
        console.log(currentFrameDetected);
        if (frameInfo.frameId !== null && !currentFrameDetected){
            window.frameDetected = true;
            console.log('Detected a frame for clicked element');
            console.log(frameInfo.frameId);
            setFrameDetected(true);
            window.recordedEvents.push(['frame', Date.now(), frameInfo.frameId]);
        } else if (frameInfo.frameId === null && currentFrameDetected){
            window.frameDetected = false;
            console.log('You have now left the frame to the parent body');
            setFrameDetected(false);
            window.recordedEvents.push(['frame', Date.now(), 'parent']);
        }
        window.recordedEvents.push(['scroll', Date.now(), xpath]);
        sendEventsToServerSync();  
    });

    let draggedElementXpath = null;
    document.addEventListener('dragstart', function(e) {
        if (window.isPaused) return;
        draggedElementXpath = computeXPath(e.target);
        var frameInfo = getFrameInfo(e.target);
        console.log(frameInfo);
        var currentFrameDetected = getFrameDetected(); // Get the current state from localStorage
        console.log(currentFrameDetected);
        if (frameInfo.frameId !== null && !currentFrameDetected){
            window.frameDetected = true;
            console.log('Detected a frame for clicked element');
            console.log(frameInfo.frameId);
            setFrameDetected(true);
            window.recordedEvents.push(['frame', Date.now(), frameInfo.frameId]);
        } else if (frameInfo.frameId === null && currentFrameDetected){
            window.frameDetected = false;
            console.log('You have now left the frame to the parent body');
            setFrameDetected(false);
            window.recordedEvents.push(['frame', Date.now(), 'parent']);
        }
        window.recordedEvents.push(['dragStart', Date.now(), draggedElementXpath]);
        sendEventsToServerSync();  
    });

    document.addEventListener('drop', function(event) {
        if (window.isPaused) return;
        event.preventDefault();
        let dropTargetXpath = computeXPath(event.target); 
        console.log('Dropped on: ' + dropTargetXpath);
        var frameInfo = getFrameInfo(e.target);
        console.log(frameInfo);
        var currentFrameDetected = getFrameDetected(); // Get the current state from localStorage
        console.log(currentFrameDetected);
        if (frameInfo.frameId !== null && !currentFrameDetected){
            window.frameDetected = true;
            console.log('Detected a frame for clicked element');
            console.log(frameInfo.frameId);
            setFrameDetected(true);
            window.recordedEvents.push(['frame', Date.now(), frameInfo.frameId]);
        } else if (frameInfo.frameId === null && currentFrameDetected){
            window.frameDetected = false;
            console.log('You have now left the frame to the parent body');
            setFrameDetected(false);
            window.recordedEvents.push(['frame', Date.now(), 'parent']);
        }
        window.recordedEvents.push(['drop', Date.now(), dropTargetXpath]);
        sendEventsToServerSync();
        draggedElementXpath = null;
    });

    document.addEventListener('dragover', function(event) {
        event.preventDefault(); 
    });

    function getTextByXPath(xpath) {
        var result = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
        console.log('The result of the getText is hither');
        if (result.singleNodeValue) {
            return result.singleNodeValue.textContent;
        } else {
            return null;
        }
    }

    function computeXPathOfElementAt20Percent() {
        var yPosition = window.innerHeight * 0.36; 
        var elements = document.elementsFromPoint(window.innerWidth / 2, yPosition);
        for (var i = 0; i < elements.length; i++) {
            var xpath = computeXPath(elements[i]);
            if (xpath) {
                return xpath;
            }
        }
        return null;
    }

    recordPageLoadEvent();

    function computeXPath(element) {
        if (!element) return null;

        function escapeXPathString(str) {
            if (!str.includes("'")) return `'${str}'`;
            if (!str.includes('"')) return `"${str}"`;
            let parts = str.split("'");
            let xpathString = "concat(";
            for (let i = 0; i < parts.length; i++) {
                xpathString += `'${parts[i]}'`;
                if (i < parts.length - 1) {
                    xpathString += `, "'", `;
                }
            }
            xpathString += ")";

            return xpathString;
        }

        function isUniqueByAttribute(element, attrName) {
            let attrValue = element.getAttribute(attrName);
            if (!attrValue) return false;
            let xpath = `//${element.tagName.toLowerCase()}[@${attrName}=${escapeXPathString(attrValue)}]`;
            return document.evaluate("count(" + xpath + ")", document, null, XPathResult.ANY_TYPE, null).numberValue === 1;
        }

        function isUniqueByText(element) {
            let text = element.textContent.trim();
            if (!text) return false;
            let xpath = `//${element.tagName.toLowerCase()}[contains(text(), ${escapeXPathString(text)})]`;
            return document.evaluate("count(" + xpath + ")", document, null, XPathResult.ANY_TYPE, null).numberValue === 1;
        }

        function getChildRelativeXPath(child, parent) {
            var path = '';
            for (var current = child; current && current !== parent; current = current.parentNode) {
                let index = 1;
                for (var sibling = current.previousElementSibling; sibling; sibling = sibling.previousElementSibling) {
                    if (sibling.nodeType === 1 && sibling.tagName === current.tagName) {
                        index++;
                    }
                }
                let tagName = current.tagName.toLowerCase();
                let pathIndex = (index > 1 ? `[${index}]` : '');
                path = '/' + tagName + pathIndex + path;
            }
            return path;
        }

        // Function to generate a unique XPath using parent attributes
        function generateRelativeXPath(element) {
            var paths = [];
            var currentElement = element;

            while (currentElement && currentElement.nodeType === 1) {
                let uniqueAttributeXPath = getUniqueAttributeXPath(currentElement);
                if (uniqueAttributeXPath) {
                    paths.unshift(uniqueAttributeXPath);
                    break; // Break the loop if a unique attribute is found
                }

                let tagName = currentElement.tagName.toLowerCase();
                let index = 1;
                for (let sibling = currentElement.previousElementSibling; sibling; sibling = sibling.previousElementSibling) {
                    if (sibling.nodeType === 1 && sibling.tagName === currentElement.tagName) {
                        index++;
                    }
                }
                let pathIndex = (index > 1 ? `[${index}]` : '');
                paths.unshift(`${tagName}${pathIndex}`);

                currentElement = currentElement.parentNode;
            }

            return paths.length ? `//${paths.join('/')}` : null;
        }

        function getUniqueAttributeXPath(element) {
            const attributes = ['id', 'name', 'type', 'value', 'title', 'alt', 'col-id', 'colid', 'ref', 'role', 'ng-bind'];
            for (let attr of attributes) {
                if (isUniqueByAttribute(element, attr)) {
                    return `${element.tagName.toLowerCase()}[@${attr}='${element.getAttribute(attr)}']`;
                }
            }
            return null;
        }    

        // Special handling for svg elements
        if (element.tagName.toLowerCase() === 'svg' || element.tagName.toLowerCase() === 'path') {
            let parentElement = element.parentElement;
            if (parentElement) {
                let parentXPath = computeXPath(parentElement);
                if (parentXPath) {
                    if (parentXPath.startsWith('//')){
                        return parentXPath;
                    } else if (parentXPath.startsWith('/')){
                        return '/' + parentXPath;
                    } else {
                        return '//' + parentXPath;
                    }	
                }
            }
            return null;
        }

        const attributes = ['id', 'name', 'type', 'value', 'title', 'alt', 'col-id', 'colid', 'ref', 'role', 'ng-bind'];
        for (let attr of attributes) {
            if (isUniqueByAttribute(element, attr)) {
                return `//${element.tagName.toLowerCase()}[@${attr}='${element.getAttribute(attr)}']`;
            }
        }

        if (element.className && typeof element.className === 'string') {	
            let classes = element.className.trim().split(/\s+/);
            let combinedClassSelector = classes.join('.');
            let xpath = `//${element.tagName.toLowerCase()}[contains(@class, '${combinedClassSelector}')]`;
            if (document.evaluate("count(" + xpath + ")", document, null, XPathResult.ANY_TYPE, null).numberValue === 1) {
                return xpath;
            }
        }

        if (element.tagName.toLowerCase() !== 'i' && isUniqueByText(element)) {
            return `//${element.tagName.toLowerCase()}[contains(text(), ${escapeXPathString(element.textContent.trim())})]`;
        }

        return generateRelativeXPath(element);
        }          



}
"""

xpath_js = """
            var callback = arguments[arguments.length - 1];  // The callback function provided by Selenium

            function sendEventsToServerSync() {
                console.log("Sending the respective event to the server");
                if (window.isSending || window.recordedEvents.length === 0) {
                    return; // Do not send if a send operation is in progress or if there are no events to send
                }
                window.isSending = true;

                var xhr = new XMLHttpRequest();
                xhr.open("POST", 'http://localhost:9005/save', true);
                xhr.onreadystatechange = function() {
                    if (xhr.readyState == 4) {
                        if (xhr.status == 200) {
                            console.log('Event data sent successfully');
                        }
                        window.isSending = false;
                        window.recordedEvents = []; // Clear the recorded events after sending
                    }
                };

                xhr.setRequestHeader('Content-Type', 'application/json');
                xhr.send(JSON.stringify(window.recordedEvents));
            }

            function getFrameInfo() {
                if (window !== window.top) {
                    // Inside a frame
                    return {
                        isInFrame: true,
                        frameId: window.frameElement ? window.frameElement.id : 'unknownFrame'
                    };
                } else {
                    // Not inside a frame
                    return {
                        isInFrame: false,
                        frameId: null
                    };
                }
            }

            function isInIframe() {
                return window !== window.top;
            }

            // Function to update frameDetected in localStorage
            function setFrameDetected(value) {
                localStorage.setItem('frameDetected', value.toString());
            }

            // Function to get frameDetected from localStorage
            function getFrameDetected() {
                return localStorage.getItem('frameDetected') === 'true';
            }

            window.frameDetected = getFrameDetected();


            document.addEventListener('click', function getTextEvent(e) {
                e.preventDefault();
                e.stopPropagation();
                var xpath = computeXPath(e.target);
                var frameInfo = getFrameInfo(e.target);
                console.log(frameInfo);
                var currentFrameDetected = getFrameDetected(); // Get the current state from localStorage
                console.log(currentFrameDetected);
                if (frameInfo.frameId !== null && !currentFrameDetected){
                    window.frameDetected = true;
                    console.log('Detected a frame for clicked element');
                    console.log(frameInfo.frameId);
                    setFrameDetected(true);
                    window.recordedEvents.push(['frame', Date.now(), frameInfo.frameId]);
                    sendEventsToServerSync();
                } else if (frameInfo.frameId === null && currentFrameDetected){
                    window.frameDetected = false;
                    console.log('You have now left the frame to the parent body');
                    setFrameDetected(false);
                    window.recordedEvents.push(['frame', Date.now(), 'parent']);
                    sendEventsToServerSync();
                }
                console.log(xpath);
                callback(xpath);  // Call the callback with the XPath as the argument
            });

            function computeXPath(element) {
                if (!element) return null;

                function escapeXPathString(str) {
                    if (!str.includes("'")) return `'${str}'`;
                    if (!str.includes('"')) return `"${str}"`;
                    let parts = str.split("'");
                    let xpathString = "concat(";
                    for (let i = 0; i < parts.length; i++) {
                        xpathString += `'${parts[i]}'`;
                        if (i < parts.length - 1) {
                            xpathString += `, "'", `;
                        }
                    }
                    xpathString += ")";

                    return xpathString;
                }

                function isUniqueByAttribute(element, attrName) {
                    let attrValue = element.getAttribute(attrName);
                    if (!attrValue) return false;
                    let xpath = `//${element.tagName.toLowerCase()}[@${attrName}=${escapeXPathString(attrValue)}]`;
                    return document.evaluate("count(" + xpath + ")", document, null, XPathResult.ANY_TYPE, null).numberValue === 1;
                }

                function isUniqueByText(element) {
                    let text = element.textContent.trim();
                    if (!text) return false;
                    let xpath = `//${element.tagName.toLowerCase()}[contains(text(), ${escapeXPathString(text)})]`;
                    return document.evaluate("count(" + xpath + ")", document, null, XPathResult.ANY_TYPE, null).numberValue === 1;
                }

                function getChildRelativeXPath(child, parent) {
                    var path = '';
                    for (var current = child; current && current !== parent; current = current.parentNode) {
                        let index = 1;
                        for (var sibling = current.previousElementSibling; sibling; sibling = sibling.previousElementSibling) {
                            if (sibling.nodeType === 1 && sibling.tagName === current.tagName) {
                                index++;
                            }
                        }
                        let tagName = current.tagName.toLowerCase();
                        let pathIndex = (index > 1 ? `[${index}]` : '');
                        path = '/' + tagName + pathIndex + path;
                    }
                    return path;
                }

                // Function to generate a unique XPath using parent attributes
                function generateRelativeXPath(element) {
                    var paths = [];
                    var currentElement = element;

                    while (currentElement && currentElement.nodeType === 1) {
                        let uniqueAttributeXPath = getUniqueAttributeXPath(currentElement);
                        if (uniqueAttributeXPath) {
                            paths.unshift(uniqueAttributeXPath);
                            break; // Break the loop if a unique attribute is found
                        }

                        let tagName = currentElement.tagName.toLowerCase();
                        let index = 1;
                        for (let sibling = currentElement.previousElementSibling; sibling; sibling = sibling.previousElementSibling) {
                            if (sibling.nodeType === 1 && sibling.tagName === currentElement.tagName) {
                                index++;
                            }
                        }
                        let pathIndex = (index > 1 ? `[${index}]` : '');
                        paths.unshift(`${tagName}${pathIndex}`);

                        currentElement = currentElement.parentNode;
                    }

                    return paths.length ? `//${paths.join('/')}` : null;
                }

                function getUniqueAttributeXPath(element) {
                    const attributes = ['id', 'name', 'type', 'value', 'title', 'alt', 'col-id', 'colid', 'ref', 'role', 'ng-bind'];
                    for (let attr of attributes) {
                        if (isUniqueByAttribute(element, attr)) {
                            return `${element.tagName.toLowerCase()}[@${attr}='${element.getAttribute(attr)}']`;
                        }
                    }
                    return null;
                }    

                // Special handling for svg elements
                if (element.tagName.toLowerCase() === 'svg' || element.tagName.toLowerCase() === 'path') {
                    let parentElement = element.parentElement;
                    if (parentElement) {
                        let parentXPath = computeXPath(parentElement);
                        if (parentXPath) {
                            if (parentXPath.startsWith('//')){
                                return parentXPath;
                            } else if (parentXPath.startsWith('/')){
                                return '/' + parentXPath;
                            } else {
                                return '//' + parentXPath;
                            }	
                        }
                    }
                    return null;
                }

                const attributes = ['id', 'name', 'type', 'value', 'title', 'alt', 'col-id', 'colid', 'ref', 'role', 'ng-bind'];
                for (let attr of attributes) {
                    if (isUniqueByAttribute(element, attr)) {
                        return `//${element.tagName.toLowerCase()}[@${attr}='${element.getAttribute(attr)}']`;
                    }
                }

                if (element.className && typeof element.className === 'string') {	
                    let classes = element.className.trim().split(/\s+/);
                    let combinedClassSelector = classes.join('.');
                    let xpath = `//${element.tagName.toLowerCase()}[contains(@class, '${combinedClassSelector}')]`;
                    if (document.evaluate("count(" + xpath + ")", document, null, XPathResult.ANY_TYPE, null).numberValue === 1) {
                        return xpath;
                    }
                }

                if (element.tagName.toLowerCase() !== 'i' && isUniqueByText(element)) {
                    return `//${element.tagName.toLowerCase()}[contains(text(), ${escapeXPathString(element.textContent.trim())})]`;
                }

                return generateRelativeXPath(element);
                }
        """



get_xpath_js = """
            var callback = arguments[arguments.length - 1];  // The callback function provided by Selenium

            document.addEventListener('click', function getTextEvent(e) {
                e.preventDefault();
                e.stopPropagation();
                var xpath = computeXPath(e.target);
                console.log(xpath);
                callback(xpath);  // Call the callback with the XPath as the argument
            });

            function computeXPath(element) {
                if (!element) return null;

                function escapeXPathString(str) {
                    if (!str.includes("'")) return `'${str}'`;
                    if (!str.includes('"')) return `"${str}"`;
                    let parts = str.split("'");
                    let xpathString = "concat(";
                    for (let i = 0; i < parts.length; i++) {
                        xpathString += `'${parts[i]}'`;
                        if (i < parts.length - 1) {
                            xpathString += `, "'", `;
                        }
                    }
                    xpathString += ")";

                    return xpathString;
                }

                function isUniqueByAttribute(element, attrName) {
                    let attrValue = element.getAttribute(attrName);
                    if (!attrValue) return false;
                    let xpath = `//${element.tagName.toLowerCase()}[@${attrName}=${escapeXPathString(attrValue)}]`;
                    return document.evaluate("count(" + xpath + ")", document, null, XPathResult.ANY_TYPE, null).numberValue === 1;
                }

                function isUniqueByText(element) {
                    let text = element.textContent.trim();
                    if (!text) return false;
                    let xpath = `//${element.tagName.toLowerCase()}[contains(text(), ${escapeXPathString(text)})]`;
                    return document.evaluate("count(" + xpath + ")", document, null, XPathResult.ANY_TYPE, null).numberValue === 1;
                }

                function getChildRelativeXPath(child, parent) {
                    var path = '';
                    for (var current = child; current && current !== parent; current = current.parentNode) {
                        let index = 1;
                        for (var sibling = current.previousElementSibling; sibling; sibling = sibling.previousElementSibling) {
                            if (sibling.nodeType === 1 && sibling.tagName === current.tagName) {
                                index++;
                            }
                        }
                        let tagName = current.tagName.toLowerCase();
                        let pathIndex = (index > 1 ? `[${index}]` : '');
                        path = '/' + tagName + pathIndex + path;
                    }
                    return path;
                }

                // Function to generate a unique XPath using parent attributes
                function generateRelativeXPath(element) {
                    var paths = [];
                    var currentElement = element;

                    while (currentElement && currentElement.nodeType === 1) {
                        let uniqueAttributeXPath = getUniqueAttributeXPath(currentElement);
                        if (uniqueAttributeXPath) {
                            paths.unshift(uniqueAttributeXPath);
                            break; // Break the loop if a unique attribute is found
                        }

                        let tagName = currentElement.tagName.toLowerCase();
                        let index = 1;
                        for (let sibling = currentElement.previousElementSibling; sibling; sibling = sibling.previousElementSibling) {
                            if (sibling.nodeType === 1 && sibling.tagName === currentElement.tagName) {
                                index++;
                            }
                        }
                        let pathIndex = (index > 1 ? `[${index}]` : '');
                        paths.unshift(`${tagName}${pathIndex}`);

                        currentElement = currentElement.parentNode;
                    }

                    return paths.length ? `//${paths.join('/')}` : null;
                }

                function getUniqueAttributeXPath(element) {
                    const attributes = ['id', 'name', 'type', 'value', 'title', 'alt', 'col-id', 'colid', 'ref', 'role', 'ng-bind'];
                    for (let attr of attributes) {
                        if (isUniqueByAttribute(element, attr)) {
                            return `${element.tagName.toLowerCase()}[@${attr}='${element.getAttribute(attr)}']`;
                        }
                    }
                    return null;
                }    

                // Special handling for svg elements
                if (element.tagName.toLowerCase() === 'svg' || element.tagName.toLowerCase() === 'path') {
                    let parentElement = element.parentElement;
                    if (parentElement) {
                        let parentXPath = computeXPath(parentElement);
                        if (parentXPath) {
                            if (parentXPath.startsWith('//')){
                                return parentXPath;
                            } else if (parentXPath.startsWith('/')){
                                return '/' + parentXPath;
                            } else {
                                return '//' + parentXPath;
                            }	
                        }
                    }
                    return null;
                }

                const attributes = ['id', 'name', 'type', 'value', 'title', 'alt', 'col-id', 'colid', 'ref', 'role', 'ng-bind'];
                for (let attr of attributes) {
                    if (isUniqueByAttribute(element, attr)) {
                        return `//${element.tagName.toLowerCase()}[@${attr}='${element.getAttribute(attr)}']`;
                    }
                }

                if (element.className && typeof element.className === 'string') {	
                    let classes = element.className.trim().split(/\s+/);
                    let combinedClassSelector = classes.join('.');
                    let xpath = `//${element.tagName.toLowerCase()}[contains(@class, '${combinedClassSelector}')]`;
                    if (document.evaluate("count(" + xpath + ")", document, null, XPathResult.ANY_TYPE, null).numberValue === 1) {
                        return xpath;
                    }
                }

                if (element.tagName.toLowerCase() !== 'i' && isUniqueByText(element)) {
                    return `//${element.tagName.toLowerCase()}[contains(text(), ${escapeXPathString(element.textContent.trim())})]`;
                }

                return generateRelativeXPath(element);
                }
        """




