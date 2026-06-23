/**
 * CANTOR DASHBOARD — FRONT-END INTERACTIVE APPLICATION
 */

document.addEventListener("DOMContentLoaded", () => {
    // Global Application State
    const state = {
        activeTab: "calendar",
        selectedDate: new Date().toISOString().split('T')[0],
        selectedBookFilename: "",
        selectedKey: "",
        booksData: [],
        keyToFileMap: {}, // key -> filename map
        linterReport: null,
        activeLinterFile: "",
        currentBookletText: "",
        currentDigestText: "",
        currentRawKeyData: null,
        currentCleanKeyData: null,
        // Overrides settings state
        paschalion: localStorage.getItem("cantor-opt-paschalion") || "gregorian",
        version: localStorage.getItem("cantor-opt-version") || "stamford_2014",
        templeFeast: localStorage.getItem("cantor-opt-temple-feast") || "",
        digestMode: localStorage.getItem("cantor-opt-digest-mode") || "full",
        devMode: localStorage.getItem("cantor-opt-dev-mode") === "true",
        includeCeremonial: localStorage.getItem("cantor-opt-include-ceremonial") === "true",
        // Profiles state
        profiles: JSON.parse(localStorage.getItem("cantor-profiles") || "{}"),
        activeProfile: localStorage.getItem("cantor-active-profile") || "default",
        // Collapsible reference panel state
        referenceOpen: localStorage.getItem("cantor-reference-open") !== "false",
        selectedRefTab: localStorage.getItem("cantor-selected-ref-tab") || "doc-digest",
        parsedServices: null,
        // Roadmap state
        roadmapData: null,
        activeFeastDayIndex: null
    };

    // DOM Elements Cache
    const el = {
        // Navigation
        navBtns: document.querySelectorAll(".nav-btn"),
        tabPanels: document.querySelectorAll(".tab-panel"),
        themeToggleBtn: document.getElementById("theme-toggle-btn"),
        
        // Tab 1: Calendar
        liturgicalDateInput: document.getElementById("liturgical-date-input"),
        resolveDateBtn: document.getElementById("resolve-date-btn"),
        quickBtns: document.querySelectorAll(".quick-btn"),
        contextSpinner: document.getElementById("context-spinner"),
        contextContent: document.getElementById("context-content"),
        traceContent: document.getElementById("trace-content"),
        docTabBtns: document.querySelectorAll(".doc-tab-btn"),
        docPanels: document.querySelectorAll(".doc-panel"),
        bookletContent: document.getElementById("booklet-content"),
        digestContent: document.getElementById("digest-content"),
        printBookletBtn: document.getElementById("print-booklet-btn"),
        copyBtns: document.querySelectorAll(".copy-btn"),
        btnToggleReference: document.getElementById("btn-toggle-reference"),
        btnCloseReference: document.getElementById("btn-close-reference"),
        serviceDigestSelect: document.getElementById("service-digest-select"),
        serviceDigestContent: document.getElementById("service-digest-content"),
        
        // Tab 2: Book Browser
        bookSelect: document.getElementById("book-select"),
        keySearchInput: document.getElementById("key-search-input"),
        keyCount: document.getElementById("key-count"),
        keyList: document.getElementById("key-list"),
        viewerBookBadge: document.getElementById("viewer-book-badge"),
        viewerKeyId: document.getElementById("viewer-key-id"),
        copyRawBtn: document.getElementById("copy-raw-btn"),
        copyCleanBtn: document.getElementById("copy-clean-btn"),
        diffOriginalContent: document.getElementById("diff-original-content"),
        diffStandardizedContent: document.getElementById("diff-standardized-content"),
        
        // Tab 3: Linter
        statTotal: document.getElementById("stat-total").querySelector(".stat-num"),
        statTerminology: document.getElementById("stat-terminology").querySelector(".stat-num"),
        statPronoun: document.getElementById("stat-pronoun").querySelector(".stat-num"),
        statHieratic: document.getElementById("stat-hieratic").querySelector(".stat-num"),
        linterFileList: document.getElementById("linter-file-list"),
        linterIssueDetails: document.getElementById("linter-issue-details"),
        
        // Toast
        toast: document.getElementById("toast")
    };

    // API Base URL
    const API_BASE = "";

    // Set today's date in picker as default
    el.liturgicalDateInput.value = state.selectedDate;

    /* ==========================================================================
       THEMING SYSTEM
       ========================================================================== */
    function initTheme() {
        const savedTheme = localStorage.getItem("cantor-dashboard-theme");
        if (savedTheme === "dark") {
            document.body.classList.remove("light-theme");
            document.body.classList.add("dark-theme");
            el.themeToggleBtn.innerHTML = '<span class="toggle-icon">☀️</span> Light Mode';
        } else {
            document.body.classList.remove("dark-theme");
            document.body.classList.add("light-theme");
            el.themeToggleBtn.innerHTML = '<span class="toggle-icon">🌙</span> Dark Mode';
        }
    }

    el.themeToggleBtn.addEventListener("click", () => {
        if (document.body.classList.contains("dark-theme")) {
            document.body.classList.remove("dark-theme");
            document.body.classList.add("light-theme");
            el.themeToggleBtn.innerHTML = '<span class="toggle-icon">🌙</span> Dark Mode';
            localStorage.setItem("cantor-dashboard-theme", "light");
        } else {
            document.body.classList.remove("light-theme");
            document.body.classList.add("dark-theme");
            el.themeToggleBtn.innerHTML = '<span class="toggle-icon">☀️</span> Light Mode';
            localStorage.setItem("cantor-dashboard-theme", "dark");
        }
    });

    /* ==========================================================================
       TAB NAVIGATION
       ========================================================================== */
    function switchTab(tabId) {
        state.activeTab = tabId.replace("tab-", "");
        
        // Toggle Nav Buttons
        el.navBtns.forEach(btn => {
            if (btn.getAttribute("data-target") === tabId) {
                btn.classList.add("active");
            } else {
                btn.classList.remove("active");
            }
        });

        // Toggle Panels
        el.tabPanels.forEach(panel => {
            if (panel.id === tabId) {
                panel.classList.add("active");
            } else {
                panel.classList.remove("active");
            }
        });

        // Run hooks for specific tabs
        if (state.activeTab === "browser" && state.booksData.length === 0) {
            loadBooks();
        } else if (state.activeTab === "linter" && !state.linterReport) {
            loadLinterReport();
        } else if (state.activeTab === "roadmap") {
            loadRoadmapData();
        }
    }

    el.navBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            switchTab(btn.getAttribute("data-target"));
        });
    });

    // Document Tabs Switcher (Liturgical Calendar booklet vs digest)
    el.docTabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetId = btn.getAttribute("data-doc-target");
            
            // Toggle active tab buttons
            el.docTabBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            
            // Toggle active panels
            el.docPanels.forEach(panel => {
                if (panel.id === targetId) {
                    panel.classList.add("active");
                } else {
                    panel.classList.remove("active");
                }
            });
        });
    });

    /* ==========================================================================
       NOTIFICATION TOAST HELPER
       ========================================================================== */
    let toastTimeout;
    function showToast(message) {
        el.toast.textContent = message;
        el.toast.classList.remove("hidden");
        clearTimeout(toastTimeout);
        toastTimeout = setTimeout(() => {
            el.toast.classList.add("hidden");
        }, 2000);
    }

    function copyTextToClipboard(text, successMessage = "Copied to clipboard!") {
        if (!text) return;
        navigator.clipboard.writeText(text).then(() => {
            showToast(successMessage);
        }).catch(err => {
            console.error("Clipboard copy failed: ", err);
            showToast("Failed to copy text.");
        });
    }

    // Bind document booklet copy buttons
    el.copyBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const sourceId = btn.getAttribute("data-clipboard-source");
            if (sourceId === "booklet-content") {
                copyTextToClipboard(state.currentBookletText, "Booklet text copied!");
            } else if (sourceId === "digest-content") {
                copyTextToClipboard(state.currentDigestText, "Digest markdown copied!");
            } else if (sourceId === "service-digest-content") {
                const serviceSelect = document.getElementById("service-digest-select");
                const selectedService = serviceSelect ? serviceSelect.value : "all";
                if (selectedService === "all") {
                    copyTextToClipboard(state.currentDigestText, "Full Digest copied!");
                } else {
                    let combinedText = "";
                    let found = false;
                    if (state.parsedServices) {
                        if (state.parsedServices[selectedService]) {
                            found = true;
                            combinedText = state.parsedServices[selectedService];
                        } else {
                            Object.entries(state.parsedServices).forEach(([key, text]) => {
                                const genericName = getGenericServiceName(key);
                                let matches = false;
                                if (genericName === selectedService ||
                                    (selectedService === "Vespers" && genericName === "Vesperal Liturgy") ||
                                    (selectedService === "Divine Liturgy" && genericName === "Vesperal Liturgy")) {
                                    matches = true;
                                }
                                if (matches) {
                                    found = true;
                                    combinedText += `## ${key}\n\n${text}\n\n`;
                                }
                            });
                        }
                    }
                    if (found) {
                        copyTextToClipboard(combinedText.trim(), `${selectedService} text copied!`);
                    } else {
                        showToast(`No text found for ${selectedService}`);
                    }
                }
            }
        });
    });

    if (el.serviceDigestSelect) {
        el.serviceDigestSelect.addEventListener("change", () => {
            renderServiceDigestContent();
        });
    }

    // Print booklet view
    el.printBookletBtn.addEventListener("click", () => {
        window.print();
    });

    /* ==========================================================================
       DATE RESOLVER PANEL
       ========================================================================== */
    async function resolveDate(dateStr) {
        state.selectedDate = dateStr;
        el.liturgicalDateInput.value = dateStr;
        
        // Show Spinner
        el.contextSpinner.classList.remove("hidden");
        el.contextContent.innerHTML = "";
        el.traceContent.innerHTML = '<p class="placeholder-text">Loading trace logs...</p>';
        el.bookletContent.innerHTML = '<p class="placeholder-text">Loading Cantor booklet...</p>';
        el.digestContent.innerHTML = '<p class="placeholder-text">Loading Typikon instructions...</p>';
        
        try {
            const params = new URLSearchParams({
                date: dateStr,
                paschalion: state.paschalion,
                version: state.version,
                temple_feast: state.templeFeast,
                digest_mode: state.digestMode,
                include_ceremonial: state.includeCeremonial
            });
            const response = await fetch(`${API_BASE}/api/resolve?${params.toString()}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            
            if (data.error) {
                renderErrorState(data.error, data.traceback);
                return;
            }

            renderLiturgicalContext(data.context, data.rubrics, data.fasting, data.ceremonial);
            renderTraceLogs(data.rubrics.trace);
            
            state.currentBookletText = data.booklet;
            state.currentDigestText = data.digest;
            
            renderBookletHtml(data.booklet);
            renderDigestHtml(data.digest);
            
            state.parsedServices = parseServiceDigest(data.digest);
            renderServiceDigestDropdown();
            renderServiceDigestContent();
            updateReferenceLayout();
            
        } catch (err) {
            console.error("Error resolving date: ", err);
            renderErrorState(err.message, err.stack);
        } finally {
            el.contextSpinner.classList.add("hidden");
        }
    }

    function renderErrorState(message, traceback) {
        el.contextContent.innerHTML = `
            <div style="color: var(--rubric-color); font-weight: bold; padding: 12px 0;">
                ⚠ Error Resolving Date
            </div>
            <p style="font-size: 0.85rem; line-height: 1.4;">${message}</p>
        `;
        el.traceContent.innerHTML = traceback ? 
            `<div class="trace-line warn">${traceback}</div>` : 
            `<div class="trace-line warn">Failed to communicate with local Typikon backend engine. Make sure python server is running on port 8080.</div>`;
        el.bookletContent.innerHTML = '<p class="placeholder-text" style="color: var(--rubric-color);">Propers could not be resolved due to engine error.</p>';
        el.digestContent.innerHTML = '<p class="placeholder-text" style="color: var(--rubric-color);">Typikon digest generation failed.</p>';
        if (el.serviceDigestContent) {
            el.serviceDigestContent.innerHTML = '<p class="placeholder-text" style="color: var(--rubric-color);">Service digest generation failed.</p>';
        }
        state.parsedServices = null;
        renderServiceDigestDropdown();
    }

    function formatHumanDate(dateStr) {
        if (!dateStr) return "N/A";
        const parts = dateStr.split('-');
        if (parts.length !== 3) return dateStr;
        const months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ];
        const days = [
            "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"
        ];
        const year = parseInt(parts[0], 10);
        const monthObj = parseInt(parts[1], 10) - 1;
        const day = parseInt(parts[2], 10);
        const date = new Date(Date.UTC(year, monthObj, day));
        const dayName = days[date.getUTCDay()];
        const monthName = months[date.getUTCMonth()];
        return `${dayName}, ${monthName} ${day}, ${year}`;
    }

    function translateParadigmId(id) {
        if (!id) return "Unknown Case";
        const map = {
            "CASE_01": "Case 1 — Sunday with Simple Saint",
            "CASE_02": "Case 2 — Weekday with Simple Saint",
            "CASE_03": "Case 3 — Saturday with Simple Saint",
            "CASE_04": "Case 4 — Sunday with Polyeleos Saint",
            "CASE_05": "Case 5 — Weekday with Polyeleos Saint",
            "CASE_06": "Case 6 — Sunday with Vigil Saint",
            "CASE_07": "Case 7 — Weekday with Vigil Saint",
            "CASE_08": "Case 8 — Sunday in Forefeast/Afterfeast",
            "CASE_09": "Case 9 — Weekday in Forefeast/Afterfeast",
            "CASE_10": "Case 10 — Great Feast of the Lord",
            "CASE_11": "Case 11 — Great Feast of the Theotokos on Sunday",
            "CASE_12": "Case 12 — Great Feast of the Theotokos on Weekday",
            "CASE_13": "Case 13 — Sunday after Feast with Simple Saint",
            "CASE_14": "Case 14 — Weekday after Feast with Simple Saint",
            "CASE_15": "Case 15 — Sunday after Feast with Polyeleos Saint",
            "CASE_16": "Case 16 — Weekday after Feast with Polyeleos Saint",
            "CASE_17": "Case 17 — Sunday after Feast with Vigil Saint",
            "CASE_18": "Case 18 — Weekday after Feast with Vigil Saint",
            "CASE_19": "Case 19 — Sunday of Apodosis",
            "CASE_20": "Case 20 — Weekday of Apodosis",
            "CASE_21": "Case 21 — Sunday of Forefathers/Ancestors",
            "CASE_22": "Case 22 — Saturday of Forefathers/Ancestors"
        };
        return map[id] || id;
    }

    function getLiturgicalCategory(name) {
        if (!name) return "Saint";
        const n = name.toLowerCase();
        
        // Strip out "equal-to-the-apostles" or "equal to the apostles" for plural/category checks
        const nForPlural = n.replace(/equal[- ]to[- ]the[- ]apostles?/g, '');
        
        // Plural indicators
        let isPlural = false;
        
        // Check for plural keywords using word boundaries
        const pluralKeywords = [
            /\bmartyrs\b/, /\bapostles\b/, /\bprophets\b/, /\bvenerables\b/, 
            /\bsaints\b/, /\bfathers\b/, /\bhierarchs\b/, /\bunmercenaries\b/,
            /\bcompanions\b/, /\bothers\b/, /\bfellows\b/, /\bwomen\b/, /\bmonastics\b/
        ];
        if (pluralKeywords.some(pattern => pattern.test(nForPlural))) {
            isPlural = true;
        } else if (/\bsts\b/i.test(nForPlural)) {
            isPlural = true;
        } else if (/\band\b/i.test(nForPlural) || nForPlural.includes('&')) {
            isPlural = true;
        } else if (nForPlural.includes('those with') || nForPlural.includes('companion')) {
            isPlural = true;
        } else if (nForPlural.includes(',')) {
            const parts = nForPlural.split(',');
            if (parts.length > 1) {
                const afterComma = parts[1].trim();
                const singularTitles = ['bishop', 'pope', 'abbot', 'monk', 'nun', 'martyr', 'hierarch', 'archbishop', 'metropolitan', 'patriarch', 'priest', 'deacon', 'king', 'prince', 'writer', 'disciple', 'apostle', 'forerunner'];
                const isTitle = singularTitles.some(t => afterComma.startsWith(t));
                if (!isTitle) {
                    isPlural = true;
                }
            }
        }

        // Check categories by priority with word boundaries or substring checks
        if (/\bforerunner\b/i.test(n) || /\bjohn the baptist\b/i.test(n)) {
            return 'Prophet';
        }
        if (/\bcross\b/i.test(n)) {
            return 'Cross';
        }
        if (/\bangels?\b|\barchangels?\b/i.test(n)) {
            return 'Angels';
        }
        if (/\bfools?\b/i.test(n)) {
            return isPlural ? 'Fools for Christ' : 'Fool for Christ';
        }
        if (/\bhieromartyrs?\b/i.test(n)) {
            return isPlural ? 'Hieromartyrs' : 'Hieromartyr';
        }
        if (
            /\bvenerable[- ]martyrs?\b/i.test(n) || 
            /\bmonk[- ]martyrs?\b/i.test(n) || 
            /\bnun[- ]martyrs?\b/i.test(n) || 
            (/\bven\b\.?/i.test(n) && (/\bmart\b\.?/i.test(n) || /\bmartyr\b/i.test(n)))
        ) {
            return isPlural ? 'Venerable Martyrs' : 'Venerable Martyr';
        }
        if (/\bvenerable[- ]women\b|\bnuns\b/i.test(n)) {
            return 'Venerable Women';
        }
        if (/\bvenerable[- ]woman\b|\bnun\b/i.test(n)) {
            return 'Venerable Woman';
        }
        if (
            /\bven\b\.?/i.test(n) || /\bvenerables?\b/i.test(n) || 
            /\babbots?\b|\bmonastics?\b|\bmonks?\b/i.test(n)
        ) {
            return isPlural ? 'Venerables' : 'Venerable';
        }
        if (
            /\bbp\b\.?|\bbishops?\b|\bhierarchs?\b/i.test(n) || 
            /\barchbishops?\b|\bmetropolitans?\b|\bpatriarchs?\b|\bpopes?\b/i.test(n)
        ) {
            return isPlural ? 'Hierarchs' : 'Hierarch';
        }
        if (/\bmartyresses\b|\bwomen[- ]martyrs\b/i.test(n)) {
            return 'Women Martyrs';
        }
        if (/\bmartyress\b|\bwoman[- ]martyr\b/i.test(n)) {
            return 'Woman Martyr';
        }
        if (
            /\bmart\b\.?/i.test(n) || /\bmartyrs?\b/i.test(n) || 
            /\bgreat[- ]martyrs?\b|\bgreatmartyrs?\b|\bprotomartyrs?\b/i.test(n)
        ) {
            return isPlural ? 'Martyrs' : 'Martyr';
        }
        if (
            /\bap\b\.?|\bapostles?\b|\bevangelists?\b/i.test(n)
        ) {
            return isPlural ? 'Apostles' : 'Apostle';
        }
        if (/\bprophets?\b|\bprophetesses?\b|\bprop\b\.?/i.test(n)) {
            return isPlural ? 'Prophets' : 'Prophet';
        }
        if (/unmercenar/i.test(n)) {
            return isPlural ? 'Unmercenaries' : 'Unmercenary';
        }
        if (/\bfathers\b/i.test(n)) {
            return 'Holy Fathers';
        }
        
        return isPlural ? 'Saints' : 'Saint';
    }

    function translateRankCode(code) {
        if (!code) return '<span class="badge badge-rank rank-minor">N/A</span>';
        const cleanCode = code.trim();
        const map = {
            "[LORD]": "Great Feast of Our Lord",
            "[MOG]": "Great Feast of the Theotokos",
            "[VIGIL]": "Vigil Rank Feast",
            "[POL]": "Polyeleos Rank Feast",
            "[GT DOX]": "Great Doxology Feast",
            "[6 SM]": "Six-Stichera (Simple) Feast",
            "[4 A+G]": "Four-Stichera (with Apostle & Gospel)",
            "[4 NO]": "Simple Weekday (No Troparion/Kontakion)",
            "[4 TR]": "Simple Weekday (with Troparion)"
        };
        const desc = map[cleanCode];
        const isMajor = ["[LORD]", "[MOG]", "[VIGIL]", "[POL]"].includes(cleanCode);
        const badgeClass = isMajor ? "rank-major" : "rank-minor";
        
        if (desc) {
            return `<span class="badge-rank ${badgeClass}" title="${desc}">${cleanCode} &mdash; ${desc}</span>`;
        }
        return `<span class="badge-rank rank-minor">${cleanCode}</span>`;
    }

    function cleanLiturgicalText(text) {
        if (!text) return "";
        let clean = text.trim();
        if (clean.endsWith('.')) {
            clean = clean.slice(0, -1);
        }
        return clean;
    }

    function formatOutlines(outlines) {
        if (!outlines) return "Default";
        if (Array.isArray(outlines)) {
            return outlines.map(o => typeof o === 'string' ? o.replace(/"/g, '') : o).join(', ');
        }
        if (typeof outlines === 'string') {
            return outlines.replace(/"/g, '');
        }
        return JSON.stringify(outlines).replace(/"/g, '');
    }

    function formatFastingBadge(fasting) {
        if (!fasting) return '<span class="badge-fast fast-no_fast">No Fast</span>';
        const type = fasting.type || "no_fast";
        const note = fasting.note || "No fasting restrictions";
        const citation = fasting.citation || "";
        let typeLabel = type.replace(/_/g, ' ');
        typeLabel = typeLabel.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
        const titleText = citation ? `${note} (${citation})` : note;
        return `<span class="badge-fast fast-${type}" title="${titleText}">${typeLabel}</span>`;
    }

    function formatColorBadge(vestment) {
        if (!vestment) return '<span class="badge-color color-gold">Gold</span>';
        const color = vestment.color || "gold";
        const alt = vestment.alt || "";
        const citation = vestment.citation || "";
        let label = color.replace(/_/g, ' ');
        label = label.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
        if (alt) {
            let altLabel = alt.replace(/_/g, ' ');
            altLabel = altLabel.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
            label += ` / ${altLabel}`;
        }
        return `<span class="badge-color color-${color}" title="${citation}">${label}</span>`;
    }

    function formatProstrations(prostrations) {
        if (!prostrations) return "Allowed";
        if (prostrations.forbidden) {
            return `<span style="color: var(--text-muted); font-size: 0.85rem;" title="${prostrations.reason}">Forbidden</span>`;
        }
        return `<span style="color: var(--text-primary); font-weight: 500; font-size: 0.85rem;" title="${prostrations.reason}">Allowed</span>`;
    }

    function getLiturgicalBookInfo(ctx) {
        if (ctx.triodion_book && ctx.menaion_book && ctx.menaion_class) {
            return {
                triodion: ctx.triodion_book,
                menaion: ctx.menaion_book,
                menaionDetail: ctx.menaion_class
            };
        }

        // 1. Determine Triodion Book
        let triodionBook = "N/A";
        const seasonId = ctx.season_id || "";
        const season = ctx.season || "";
        if (seasonId === "triodion" || season === "lent" || season === "pre_lent") {
            triodionBook = "Lenten";
        } else if (seasonId === "pentecostarion" || season === "pascha") {
            triodionBook = "Floral";
        }

        // 2. Determine Menaion Book and Rank/Class
        let menaionBook = "N/A";
        let menaionDetail = "";
        const rankCode = ctx.fixed_rank_code || ctx.dolnytsky_rank_code || "";
        const rankVal = ctx.rank !== undefined ? parseInt(ctx.rank) : 5;
        
        // Categorize Saint Types
        function getSaintTypes(str) {
            const s = (str || "").toLowerCase();
            const types = [];
            if (s.includes("martyrs") || s.includes("мученики")) {
                types.push("Martyrs");
            } else if (s.includes("martyr") || s.includes("мученик") || s.includes("passion-bearer")) {
                types.push("Martyr");
            }
            if (s.includes("bishops") || s.includes("hierarchs") || s.includes("святители")) {
                types.push("Hierarchs");
            } else if (s.includes("bishop") || s.includes("hierarch") || s.includes("святитель") || s.includes("pope") || s.includes("archbishop") || s.includes("metropolitan")) {
                types.push("Hierarch");
            }
            if (s.includes("apostles") || s.includes("апостолы")) {
                types.push("Apostles");
            } else if (s.includes("apostle") || s.includes("апостол") || s.includes("evangelist")) {
                types.push("Apostle");
            }
            if (s.includes("venerables") || s.includes("преподобные") || s.includes("monks") || s.includes("nuns")) {
                types.push("Venerables");
            } else if (s.includes("venerable") || s.includes("преподобн") || s.includes("monk") || s.includes("nun") || s.includes("hermit") || s.includes("ascetic")) {
                types.push("Venerable");
            }
            if (s.includes("prophets") || s.includes("пророки")) {
                types.push("Prophets");
            } else if (s.includes("prophet") || s.includes("пророк")) {
                types.push("Prophet");
            }
            if (types.length === 0) {
                types.push("Saint");
            }
            return types;
        }

        let saintTypes = [];
        if (ctx.saints && ctx.saints.length > 0) {
            ctx.saints.forEach(s => {
                const sTypes = getSaintTypes(s.name);
                sTypes.forEach(t => {
                    if (!saintTypes.includes(t)) {
                        saintTypes.push(t);
                    }
                });
            });
        } else {
            saintTypes = getSaintTypes(ctx.dolnytsky_commemoration || "");
        }

        // Check if Festal vs General
        const isFestal = ["[LORD]", "[MOG]", "[VIGIL]", "[POL]"].includes(rankCode) || rankVal <= 2;
        
        let classNum = "V";
        let classLabel = "Simple";
        if (rankCode === "[LORD]" || rankCode === "[MOG]" || rankVal === 1) {
            classNum = "I";
            classLabel = "Great Feast";
        } else if (rankCode === "[VIGIL]" || rankVal === 2) {
            classNum = "II";
            classLabel = "Vigil";
        } else if (rankCode === "[POL]" || rankVal === 3) {
            classNum = "III";
            classLabel = "Polyeleos";
        } else if (rankCode === "[GT DOX]" || rankVal === 4) {
            classNum = "IV";
            classLabel = "Great Doxology";
        } else if (rankCode === "[6 SM]") {
            classNum = "V";
            classLabel = "Six-Stichera";
        } else {
            classNum = "V";
            classLabel = "Simple";
        }
        
        menaionDetail = `Class ${classNum} — ${classLabel}`;
        
        if (isFestal) {
            menaionBook = "Festal";
        } else {
            menaionBook = "General";
        }

        return {
            triodion: triodionBook,
            menaion: menaionBook,
            menaionDetail: menaionDetail
        };
    }

    function formatServiceKey(key) {
        if (!key) return "";
        let cleaned = key.replace(/_/g, ' ');
        cleaned = cleaned.replace(/structure /i, "");
        cleaned = cleaned.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
        return cleaned;
    }

    function getLiturgicalCombination(rubrics) {
        const vars = rubrics.variables || {};
        const overs = rubrics.overrides || {};
        
        const vType = overs.vespers_type || vars.vespers_type || "daily_vespers";
        const mType = overs.matins_type || vars.matins_type || "daily_matins";
        const lType = overs.liturgy_type || vars.liturgy_type || "liturgy_chrysostom";
        const hType = overs.hours_type || vars.hours_type || "structure_standard";
        
        const vespersMap = {
            "daily_vespers": "Daily Vespers",
            "great_vespers": "Great Vespers",
            "great_vespers_vigil": "Great Vespers (Vigil)",
            "lenten_vespers": "Lenten Vespers",
            "presanctified_vespers": "Presanctified Vespers",
            "vespers_with_vigil": "Great Vespers (Vigil)"
        };
        
        const matinsMap = {
            "daily_matins": "Daily Matins",
            "great_matins": "Great Matins",
            "great_matins_vigil": "Great Matins (Vigil)",
            "lenten_matins": "Lenten Matins",
            "lenten_matins_weekday": "Lenten Matins",
            "bridegroom_matins": "Bridegroom Matins",
            "passion_matins": "Passion Matins",
            "tomb_matins": "Tomb Matins",
            "bright_matins": "Bright Matins"
        };
        
        const liturgyMap = {
            "liturgy_chrysostom": "St. John Chrysostom",
            "liturgy_basil": "St. Basil the Great",
            "presanctified_liturgy": "Presanctified Liturgy",
            "presanctified": "Presanctified Liturgy",
            "aliturgical": "Aliturgical (No Liturgy)"
        };
        
        const hoursMap = {
            "structure_standard": "Standard Hours",
            "structure_lenten": "Lenten Hours",
            "structure_royal": "Royal Hours",
            "structure_paschal": "Paschal Hours"
        };
        
        const vLabel = vespersMap[vType] || formatServiceKey(vType);
        const mLabel = matinsMap[mType] || formatServiceKey(mType);
        const lLabel = liturgyMap[lType] || formatServiceKey(lType);
        const hLabel = hoursMap[hType] || formatServiceKey(hType);
        
        // Check if it's an All-Night Vigil (Great Vespers + Great Matins combined)
        const isVigil = (vType === "great_vespers" || vType === "great_vespers_vigil" || vType === "vespers_with_vigil") && 
                        (mType === "great_matins" || mType === "great_matins_vigil");
        
        if (isVigil) {
            return `All-Night Vigil (${lLabel})`;
        }
        
        return `${vLabel} + ${mLabel} + ${lLabel}`;
    }

    function renderLiturgicalContext(ctx, rubrics, fasting, ceremonial) {
        let html = "";
        
        // General Info
        html += `<div class="context-section-header">Calendar Instance</div>`;
        html += `<div class="context-row" title="Standard civil calendar date (Gregorian) used to map the fixed Menaion cycle."><span class="context-label">Civil Date</span><span class="context-val">${formatHumanDate(ctx.date)}</span></div>`;
        
        const seasonVal = ctx.season || "ordinary";
        const seasonClean = seasonVal.replace('_', ' ');
        html += `<div class="context-row" title="Dolnytsky Typik Part V: Represents the seasonal periods of the liturgical year (Ordinary, Lenten, Paschal/Floral)."><span class="context-label">Liturgical Season</span><span class="context-val"><span class="badge-season season-${seasonVal}">${seasonClean}</span></span></div>`;
        
        const toneVal = ctx.tone !== undefined ? `Tone ${ctx.tone}` : "None";
        const toneHtml = ctx.tone !== undefined ? `<span class="badge-tone">${toneVal}</span>` : `<span style="color: var(--text-muted);">None</span>`;
        html += `<div class="context-row" title="Ordo §14: The weekly Resurrection Tone from the Octoechos (8-tone cycle) used to select service music."><span class="context-label">Octoechos Tone</span><span class="context-val">${toneHtml}</span></div>`;
        
        const eothVal = ctx.eothinon_number ? `Eothinon ${ctx.eothinon_number}` : "None";
        const eothHtml = ctx.eothinon_number ? `<span class="badge-eothinon">${eothVal}</span>` : `<span style="color: var(--text-muted);">None</span>`;
        html += `<div class="context-row" title="Ordo §78 / Orthros: The Resurrection Gospel readings assigned sequentially to Sunday Matins."><span class="context-label">Eothinon Gospel</span><span class="context-val">${eothHtml}</span></div>`;
        
        // Fasting Discipline Row
        html += `<div class="context-row" title="Particular Law of the UGCC (Can. 115): Fasting regulations and abstinence for the eparchy (Stamford recension)."><span class="context-label">Fasting Discipline</span><span class="context-val">${formatFastingBadge(fasting)}</span></div>`;
        
        // Liturgical Source Books & Classification
        html += `<div class="context-section-header">Source Books & Classification</div>`;
        const bookInfo = getLiturgicalBookInfo(ctx);
        if (bookInfo.triodion !== "N/A") {
            html += `<div class="context-row" title="Dolnytsky Typik Part III / Lenten and Floral Books: The movable cycle service book used for Lent (Lenten Triodion) or Eastertide (Pentecostarion/Floral)."><span class="context-label">Triodion</span><span class="context-val">${bookInfo.triodion}</span></div>`;
        }
        html += `<div class="context-row" title="Dolnytsky Typik Part III: The book source containing the fixed cycle saint commemorations (General vs Festal Menaion)."><span class="context-label">Menaion</span><span class="context-val">${bookInfo.menaion}</span></div>`;
        

        
        // Rank & Commemoration
        html += `<div class="context-section-header">Commemoration & Class</div>`;
        const code = ctx.fixed_rank_code || ctx.dolnytsky_rank_code || "";
        html += `<div class="context-row" title="Dolnytsky Typik Part III: The canonical rank code indicating the liturgical solemnity of the saint (e.g. [4 TR] = simple weekday with troparion)."><span class="context-label">Rank Code</span><span class="context-val">${translateRankCode(code)}</span></div>`;
        html += `<div class="context-row" title="UGCC Liturgical Directory: The solemnity class (Class I-V) governing the structure of Vespers, Matins, and Liturgy."><span class="context-label">Class</span><span class="context-val">${bookInfo.menaionDetail}</span></div>`;
        
        const caseLabel = translateParadigmId(ctx.paradigm_id);
        html += `<div class="context-row" title="The resolved collision paradigm from Dolnytsky Part V, governing how the Octoechos and Menaion parts are combined on this specific day."><span class="context-label">Rubrics Case</span><span class="context-val">${caseLabel}</span></div>`;
        
        const commVal = cleanLiturgicalText(ctx.dolnytsky_commemoration || "None");
        let titleVal = "Standard Daily Services";
        
        const vars = rubrics.variables || {};
        const overs = rubrics.overrides || {};
        const vType = overs.vespers_type || vars.vespers_type || "daily_vespers";
        const mType = overs.matins_type || vars.matins_type || "daily_matins";
        const lType = overs.liturgy_type || vars.liturgy_type || "liturgy_chrysostom";
        const hType = overs.hours_type || vars.hours_type || "structure_standard";
        
        // Check for specific special service structures
        if (mType === "bridegroom_matins") {
            titleVal = "Bridegroom Matins";
        } else if (mType === "passion_matins") {
            titleVal = "Passion Matins";
        } else if (mType === "tomb_matins") {
            titleVal = "Tomb Matins";
        } else if (mType === "bright_matins") {
            titleVal = "Bright Matins";
        } else if (hType === "structure_royal") {
            const dateStr = ctx.date || "";
            if (dateStr.includes("-01-05") || dateStr.includes("-01-02") || dateStr.includes("-01-03") || dateStr.includes("-01-04")) {
                titleVal = "Royal Hours of Theophany";
            } else if (dateStr.includes("-12-24") || dateStr.includes("-12-22") || dateStr.includes("-12-23")) {
                titleVal = "Royal Hours of Nativity";
            } else {
                titleVal = "Royal Hours of Great Friday";
            }
        } else if (lType === "presanctified_liturgy" || lType === "presanctified") {
            titleVal = "Liturgy of the Presanctified Gifts";
        } else {
            const rankVal = ctx.rank !== undefined ? parseInt(ctx.rank) : 5;
            const code = ctx.fixed_rank_code || ctx.dolnytsky_rank_code || "";
            const isLordOrTheotokosFeast = code === "[LORD]" || code === "[MOG]" || code === "LORD" || code === "THEOTOKOS";
            
            if (isLordOrTheotokosFeast || rankVal === 1) {
                titleVal = cleanLiturgicalText(ctx.dolnytsky_title || "Great Feast");
            } else if (code === "[VIGIL]" || rankVal === 2) {
                titleVal = `Vigil Service (${cleanLiturgicalText(ctx.dolnytsky_title)})`;
            } else if (ctx.day_of_week === 0) {
                titleVal = "Standard Sunday Services";
            } else {
                titleVal = "Standard Daily Services";
            }
        }
        
        html += `<div class="context-row" title="Dolnytsky Typik Part V: The official liturgical title of the day's celebration."><span class="context-label">Service Title</span><span class="context-val" style="max-width: 65%; word-break: break-word;">${titleVal}</span></div>`;
        
        if (commVal === "None") {
            html += `<div class="context-row" title="Menaion Fixed Cycle: The list of saints commemorated today."><span class="context-label">Commemorations</span><span class="context-val" style="color: var(--text-muted);">None</span></div>`;
        } else {
            const parts = commVal.replace(/\.$/, "")
                .split(/\s+and\s+|\s+&\s+|;|(?<!\bSt)(?<!\bSts)(?<!\bVen)(?<!\bBp)(?<!\bAp)(?<!\bAps)(?<!\bMetr)(?<!\bArchbp)(?<!\bPatr)(?<!\bMart)(?<!\bProp)\.\s+/i)
                .map(p => p.trim())
                .filter(p => p.length > 0);
            
            const count = parts.length;
            const label = count > 1 ? "Commemorations" : "Commemoration";
            const getCat = (idx) => (ctx.saint_categories && ctx.saint_categories[idx]) || getLiturgicalCategory(parts[idx]);
            
            // Row 1: Commemoration(s) | Count
            html += `<div class="context-row" title="The total count of active saint commemorations resolved for this service."><span class="context-label">${label}</span><span class="context-val">${count}</span></div>`;
            
            // Row 2: Primary | First Saint
            if (count >= 1) {
                const cat = getCat(0);
                html += `<div class="context-row" title="The primary saint commemoration of the day. This saint takes liturgical precedence (e.g. Troparion sung first, primary Matins canon)."><span class="context-label">Primary</span><span class="context-val" style="max-width: 65%; word-break: break-word; display: flex; align-items: center; justify-content: flex-end;"><span>${parts[0]}</span><span class="badge badge-category">${cat}</span></span></div>`;
            }
            
            // Row 3: Secondary | Second Saint (if applicable)
            if (count >= 2) {
                const cat = getCat(1);
                html += `<div class="context-row" title="The secondary saint commemoration of the day. Appended after the primary commemoration."><span class="context-label">Secondary</span><span class="context-val" style="max-width: 65%; word-break: break-word; display: flex; align-items: center; justify-content: flex-end;"><span>${parts[1]}</span><span class="badge badge-category">${cat}</span></span></div>`;
            }
            
            // Support for third saint if they exist (though Dolnytsky limit is 2, just in case)
            for (let i = 2; i < count; i++) {
                const cat = getCat(i);
                html += `<div class="context-row" title="Additional saint commemoration."><span class="context-label">Saint ${i+1}</span><span class="context-val" style="max-width: 65%; word-break: break-word; display: flex; align-items: center; justify-content: flex-end;"><span>${parts[i]}</span><span class="badge badge-category">${cat}</span></span></div>`;
            }
        }
        
        // Ceremonial Settings
        if (ceremonial) {
            html += `<div class="context-section-header">Ceremonial Settings</div>`;
            html += `<div class="context-row" title="Ordo §22–§24 / Dolnytsky Part I, Ch. 5: Canonical vestment color (e.g., Red for Martyrs, Gold/White for Hierarchs/Saints)."><span class="context-label">Liturgical Color</span><span class="context-val">${formatColorBadge(ceremonial.vestment)}</span></div>`;
            html += `<div class="context-row" title="Ordo §12 / Dolnytsky Part I, Ch. 12: Regulates full bows. Prostrations are forbidden on Sundays, Great Feasts, and during Eastertide."><span class="context-label">Prostrations</span><span class="context-val">${formatProstrations(ceremonial.prostrations)}</span></div>`;
            const variantLabel = ceremonial.clergy_variant ? ceremonial.clergy_variant.label : "Standard";
            const variantRef = ceremonial.clergy_variant ? `Ordo ${ceremonial.clergy_variant.ordo_ref}${ceremonial.clergy_variant.ordo_range ? ' (' + ceremonial.clergy_variant.ordo_range + ')' : ''}` : "";
            const clergyTooltip = `Ordo §28: Normative liturgical variant. Simple Class V weekdays are served by a single priest and deacon, without concelebrating priests. Reference: ${variantRef}`;
            html += `<div class="context-row" title="${clergyTooltip}"><span class="context-label">Clergy Variant</span><span class="context-val" style="font-size: 0.85rem;">${variantLabel}</span></div>`;
        }

        // Rubrics Resolution Outputs
        html += `<div class="context-section-header">Rubrics Outcomes</div>`;
        const outlinesVal = formatOutlines(rubrics.overrides.outlines || rubrics.variables.outlines || "Default");
        html += `<div class="context-row" title="Engine Resolvers: The structural outlines chosen by the rubric engine to generate this service booklet."><span class="context-label">Selected Outlines</span><span class="context-val" style="font-family: var(--font-mono); font-size: 0.8rem;">${outlinesVal}</span></div>`;
        
        el.contextContent.innerHTML = html;
    }

    function renderTraceLogs(trace) {
        if (!trace || trace.length === 0) {
            el.traceContent.innerHTML = '<p class="placeholder-text">No engine trace logs emitted for this resolution.</p>';
            return;
        }

        let html = "";
        trace.forEach(line => {
            let className = "info";
            const lower = line.toLowerCase();
            if (lower.includes("warn") || lower.includes("fail") || lower.includes("error")) {
                className = "warn";
            } else if (lower.includes("debug") || lower.includes("resolving") || lower.includes("loading")) {
                className = "debug";
            }
            html += `<div class="trace-line ${className}">${escapeHtml(line)}</div>`;
        });
        el.traceContent.innerHTML = html;
        el.traceContent.scrollTop = 0;
    }

    function renderBookletHtml(text) {
        if (!text) {
            el.bookletContent.innerHTML = '<p class="placeholder-text">Empty booklet content.</p>';
            return;
        }

        // Clean double carriage returns and split into blocks/paragraphs
        const paragraphs = text.split(/\r?\n\r?\n/);
        let html = "";
        let isFirstParagraph = true;

        paragraphs.forEach((p, idx) => {
            p = p.trim();
            if (!p) return;

            // If the paragraph is already HTML (starts with '<'), render it directly
            if (p.startsWith("<")) {
                if (p.includes('class="title-large"')) {
                    isFirstParagraph = true;
                }
                html += p;
                return;
            }

            // Check if paragraph is a section header (e.g. --- VESPERS ---)
            if (p.startsWith("---") && p.endsWith("---")) {
                const headerText = p.replace(/^-+\s*/, "").replace(/\s*-+$/, "");
                html += `<div class="title-large">${escapeHtml(headerText)}</div>`;
                isFirstParagraph = true; // Apply drop cap to the next paragraph
                return;
            }

            // Check if paragraph is a minor title (e.g. == Lord I Have Cried ==)
            if (p.startsWith("==") && p.endsWith("==")) {
                const titleText = p.replace(/^==\s*/, "").replace(/\s*==$/, "");
                html += `<div class="title-medium">${escapeHtml(titleText)}</div>`;
                return;
            }
            
            // Check if paragraph is a rubric instructions block
            if (p.startsWith(">>>") && p.endsWith("<<<")) {
                const rubricText = p.replace(/^>>>\s*RUBRIC:\s*/i, "").replace(/\s*<<<$/, "");
                html += `<span class="rubric">${escapeHtml(rubricText)}</span>`;
                return;
            }
            if (p.includes(">>> RUBRIC:")) {
                // If it contains rubric inside line
                let cleaned = escapeHtml(p);
                cleaned = cleaned.replace(/&gt;&gt;&gt;\s*RUBRIC:(.*?)&lt;&lt;&lt;/gi, '<span class="rubric">$1</span>');
                html += `<p>${cleaned}</p>`;
                return;
            }

            let escapedP = escapeHtml(p);

            // Parse Markdown bold **text** -> <strong>text</strong>
            escapedP = escapedP.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            // Parse Markdown italic *text* -> <em>text</em>
            escapedP = escapedP.replace(/\*(.*?)\*/g, '<em>$1</em>');

            // Handle Actor formatting like [PRIEST]: [DEACON]: etc.
            // Match [ACTOR]: and wrap in styled tags
            const actorRegex = /^\[([A-Z0-9_ -]+)\]:/i;
            const match = escapedP.match(actorRegex);
            if (match) {
                const actorName = match[1];
                const restText = escapedP.substring(match[0].length).trim();
                escapedP = `<span class="actor">${actorName}</span> ${restText}`;
            }

            // Replace line breaks inside paragraphs
            escapedP = escapedP.replace(/\n/g, "<br>");

            // Highlight blessing cross symbols and bowls
            escapedP = escapedP.replace(/✚/g, '<span class="cross-icon" style="font-size:inherit;">✚</span>');

            // Apply drop cap class to first text paragraph of a section
            if (isFirstParagraph && !match && !p.startsWith("DATE:") && !p.startsWith("FEAST:") && !p.startsWith("<") && !p.startsWith("[")) {
                html += `<p class="drop-cap">${escapedP}</p>`;
                isFirstParagraph = false;
            } else {
                html += `<p>${escapedP}</p>`;
            }
        });

        el.bookletContent.innerHTML = html;
        el.bookletContent.scrollTop = 0;
    }

    function renderDigestHtml(markdown) {
        if (!markdown) {
            el.digestContent.innerHTML = '<p class="placeholder-text">Empty typikon instructions.</p>';
            return;
        }
        el.digestContent.innerHTML = formatMarkdownHtml(markdown);
        el.digestContent.scrollTop = 0;
    }

    function parseServiceDigest(digestText) {
        const services = {};
        if (!digestText) return services;
        
        const lines = digestText.split("\n");
        let currentService = "General Info";
        services[currentService] = [];
        
        for (let line of lines) {
            const match = line.match(/^##\s*(.*?)$/);
            if (match) {
                currentService = match[1].trim();
                services[currentService] = [];
            } else {
                services[currentService].push(line);
            }
        }
        
        // Clean up empty lines
        for (let key in services) {
            let arr = services[key];
            while (arr.length > 0 && arr[0].trim() === "") {
                arr.shift();
            }
            while (arr.length > 0 && arr[arr.length - 1].trim() === "") {
                arr.pop();
            }
            if (arr.length === 0) {
                delete services[key];
            } else {
                services[key] = arr.join("\n");
            }
        }
        
        return services;
    }

    function getGenericServiceName(title) {
        const t = title.toUpperCase();
        if (t.includes("VESPERAL LITURGY")) return "Vesperal Liturgy";
        if (t.includes("VESPERS") || t.includes("VESPERAL")) return "Vespers";
        if (t.includes("COMPLINE")) return "Compline";
        if (t.includes("MIDNIGHT")) return "Midnight Office";
        if (t.includes("MATINS")) return "Matins";
        if (t.includes("FIRST HOUR")) return "First Hour";
        if (t.includes("THIRD HOUR")) return "Third Hour";
        if (t.includes("SIXTH HOUR")) return "Sixth Hour";
        if (t.includes("NINTH HOUR")) return "Ninth Hour";
        if (t.includes("HOURS")) return "Hours";
        if (t.includes("LITURGY")) return "Divine Liturgy";
        return title;
    }

    function getServiceOrderWeight(title) {
        const generic = getGenericServiceName(title);
        const order = [
            "General Info",
            "Vespers",
            "Vesperal Liturgy",
            "Compline",
            "Midnight Office",
            "Matins",
            "First Hour",
            "Third Hour",
            "Sixth Hour",
            "Ninth Hour",
            "Hours",
            "Divine Liturgy"
        ];
        const index = order.indexOf(generic);
        return index !== -1 ? index : 99;
    }

    function renderServiceDigestDropdown() {
        // Dropdown options are statically defined in index.html to preserve selection.
        if (!el.serviceDigestSelect) return;
        if (!el.serviceDigestSelect.value) {
            el.serviceDigestSelect.value = "all";
        }
    }

    function extractMetadata(text) {
        if (!text) return { cleanText: "", vestment: null, fasting: null };
        let cleanText = text;
        let vestment = null;
        let fasting = null;

        // Extract Vestment color
        const vestmentRegex = /^(?:-|\*|\*\*|\s)*Vestment colou?r:\s*(.*?)(?:\r?\n|$)/mi;
        const vestmentMatch = cleanText.match(vestmentRegex);
        if (vestmentMatch) {
            vestment = vestmentMatch[1].trim();
            cleanText = cleanText.replace(vestmentRegex, "").trim();
        }

        // Extract Fasting rule
        const fastingRegex = /^(?:-|\*|\*\*|\s)*Fasting (?:Rule)?:\s*(.*?)(?:\r?\n|$)/mi;
        const fastingMatch = cleanText.match(fastingRegex);
        if (fastingMatch) {
            fasting = fastingMatch[1].trim();
            cleanText = cleanText.replace(fastingRegex, "").trim();
        }

        return { cleanText, vestment, fasting };
    }

    function renderServiceDigestContent() {
        if (!el.serviceDigestSelect || !el.serviceDigestContent) return;
        
        const selected = el.serviceDigestSelect.value;
        
        if (selected === "all") {
            if (!state.parsedServices || Object.keys(state.parsedServices).length === 0) {
                el.serviceDigestContent.innerHTML = '<p class="placeholder-text">No service rubrics found.</p>';
                return;
            }
            
            let html = "";
            Object.entries(state.parsedServices).forEach(([serviceName, text]) => {
                const { cleanText, vestment, fasting } = extractMetadata(text);
                let badgesHtml = "";
                if (vestment || fasting) {
                    badgesHtml = `<div class="metadata-badge-container">`;
                    if (vestment) {
                        badgesHtml += `<span class="metadata-badge vestment">Vestment: ${vestment}</span>`;
                    }
                    if (fasting) {
                        badgesHtml += `<span class="metadata-badge fasting">Fasting: ${fasting}</span>`;
                    }
                    badgesHtml += `</div>`;
                }
                html += `
                    <div class="service-digest-section glass-container" style="margin-bottom: 24px; padding: 20px; border-radius: 8px;">
                        <h4 class="service-section-title" style="font-family: var(--font-heading); color: var(--gold-accent); border-bottom: 1px solid var(--card-border); padding-bottom: 8px; margin-bottom: 12px; font-size: 1.1rem; text-transform: uppercase;">${serviceName}</h4>
                        ${badgesHtml}
                        <div class="service-section-body">${formatMarkdownHtml(cleanText)}</div>
                    </div>
                `;
            });
            el.serviceDigestContent.innerHTML = html;
        } else {
            let html = "";
            let found = false;
            
            if (state.parsedServices) {
                // First check if there is an exact key match (e.g. "General Info")
                if (state.parsedServices[selected]) {
                    found = true;
                    const { cleanText, vestment, fasting } = extractMetadata(state.parsedServices[selected]);
                    let badgesHtml = "";
                    if (vestment || fasting) {
                        badgesHtml = `<div class="metadata-badge-container">`;
                        if (vestment) {
                            badgesHtml += `<span class="metadata-badge vestment">Vestment: ${vestment}</span>`;
                        }
                        if (fasting) {
                            badgesHtml += `<span class="metadata-badge fasting">Fasting: ${fasting}</span>`;
                        }
                        badgesHtml += `</div>`;
                    }
                    html += `
                        <div class="service-digest-section glass-container" style="margin-bottom: 24px; padding: 20px; border-radius: 8px;">
                            <h4 class="service-section-title" style="font-family: var(--font-heading); color: var(--gold-accent); border-bottom: 1px solid var(--card-border); padding-bottom: 8px; margin-bottom: 12px; font-size: 1.1rem; text-transform: uppercase;">${selected}</h4>
                            ${badgesHtml}
                            <div class="service-section-body">${formatMarkdownHtml(cleanText)}</div>
                        </div>
                    `;
                } else {
                    // Iterate and match based on generic name mapping
                    Object.entries(state.parsedServices).forEach(([serviceName, text]) => {
                        const genericName = getGenericServiceName(serviceName);
                        let matches = false;
                        
                        if (genericName === selected) {
                            matches = true;
                        } else if (selected === "Vespers" && genericName === "Vesperal Liturgy") {
                            matches = true;
                        } else if (selected === "Divine Liturgy" && genericName === "Vesperal Liturgy") {
                            matches = true;
                        }
                        
                        if (matches) {
                            found = true;
                            const { cleanText, vestment, fasting } = extractMetadata(text);
                            let badgesHtml = "";
                            if (vestment || fasting) {
                                badgesHtml = `<div class="metadata-badge-container">`;
                                if (vestment) {
                                    badgesHtml += `<span class="metadata-badge vestment">Vestment: ${vestment}</span>`;
                                }
                                if (fasting) {
                                    badgesHtml += `<span class="metadata-badge fasting">Fasting: ${fasting}</span>`;
                                }
                                badgesHtml += `</div>`;
                            }
                            html += `
                                <div class="service-digest-section glass-container" style="margin-bottom: 24px; padding: 20px; border-radius: 8px;">
                                    <h4 class="service-section-title" style="font-family: var(--font-heading); color: var(--gold-accent); border-bottom: 1px solid var(--card-border); padding-bottom: 8px; margin-bottom: 12px; font-size: 1.1rem; text-transform: uppercase;">${serviceName}</h4>
                                    ${badgesHtml}
                                    <div class="service-section-body">${formatMarkdownHtml(cleanText)}</div>
                                </div>
                            `;
                        }
                    });
                }
            }
            
            if (!found) {
                el.serviceDigestContent.innerHTML = `<p class="placeholder-text" style="font-family: var(--font-heading); color: var(--text-secondary); text-align: center; margin-top: 40px; font-size: 1.1rem;">${selected} is not served on this day.</p>`;
                return;
            }
            
            el.serviceDigestContent.innerHTML = html;
        }
        el.serviceDigestContent.scrollTop = 0;
    }

    // Markdown-to-HTML parser for Typikon Digest
    function formatMarkdownHtml(mdText) {
        if (!mdText) return "";
        let headerHtml = "";
        let bodyText = mdText;
        const h2Index = mdText.indexOf("##");
        if (h2Index !== -1) {
            const headerText = mdText.substring(0, h2Index);
            bodyText = mdText.substring(h2Index);
            headerHtml = `<div class="digest-header">${formatMarkdownHtmlInner(headerText)}</div>`;
        }
        return headerHtml + formatMarkdownHtmlInner(bodyText);
    }

    function formatMarkdownHtmlInner(mdText) {
        let html = escapeHtml(mdText);
        
        // Restore approved liturgical styling HTML tags after escaping
        html = html.replace(/&lt;span class=&quot;rubric&quot;&gt;(.*?)&lt;\/span&gt;/gi, '<span class="rubric">$1</span>');
        html = html.replace(/&lt;span class=&quot;sung-text&quot;&gt;(.*?)&lt;\/span&gt;/gi, '<span class="sung-text">$1</span>');
        html = html.replace(/&lt;blockquote class=&quot;verse&quot;&gt;(.*?)&lt;\/blockquote&gt;/gi, '<blockquote class="verse">$1</blockquote>');
        
        // Restore readings group styling tags after escaping
        html = html.replace(/&lt;div class=&quot;readings-group&quot;&gt;/gi, '<div class="readings-group">');
        html = html.replace(/&lt;\/div&gt;/gi, '</div>');
        html = html.replace(/&lt;span class=&quot;readings-label&quot;&gt;(.*?)&lt;\/span&gt;/gi, '<span class="readings-label">$1</span>');
        html = html.replace(/&lt;span class=&quot;readings-value&quot;&gt;(.*?)&lt;\/span&gt;/gi, '<span class="readings-value">$1</span>');
        
        // Parse citations like [Dolnytsky §12] into superscript elements
        html = html.replace(/\[([^\]]*?(?:Dolnytsky|Ordo|Typikon|Rubric|Note|Rule|§)[^\]]*?)\]/gi, '<sup class="citation-sup" title="Source Authority: $1">$1</sup>');

        // Parse GitHub-style alert blocks before other markdown replacements
        html = html.replace(/&gt;\s*\[!NOTE\]\r?\n&gt;\s*\*\*Rubric\*\*:\s*(.*?)(?=\r?\n|$)/g, '<div class="markdown-alert"><div class="markdown-alert-title">✦ Note</div><p><strong>Rubric</strong>: $1</p></div>');
        
        // Headings
        html = html.replace(/^# (.*?)$/gm, '<h1>$1</h1>');
        html = html.replace(/^## (.*?)$/gm, '<h2>$1</h2>');
        html = html.replace(/^### (.*?)$/gm, '<h3>$1</h3>');
        
        // Bold
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Italic
        html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Blockquotes
        html = html.replace(/^&gt; (.*?)$/gm, '<blockquote>$1</blockquote>');
        
        // Tables
        let lines = html.split('\n');
        let inTable = false;
        for (let i = 0; i < lines.length; i++) {
            let line = lines[i].trim();
            if (line.startsWith('|') && line.endsWith('|')) {
                if (line.includes('---')) {
                    lines[i] = '';
                    continue;
                }
                let cells = line.split('|').map(c => c.trim()).filter((c, idx, arr) => idx > 0 && idx < arr.length - 1);
                let rowHtml = cells.map(c => `<td>${c}</td>`).join('');
                if (!inTable) {
                    lines[i] = '<table><thead><tr>' + cells.map(c => `<th>${c}</th>`).join('') + '</tr></thead><tbody>';
                    inTable = true;
                } else {
                    lines[i] = `<tr>${rowHtml}</tr>`;
                }
            } else {
                if (inTable) {
                    lines[i] = '</tbody></table>' + lines[i];
                    inTable = false;
                }
            }
        }
        if (inTable) {
            lines[lines.length - 1] += '</tbody></table>';
        }
        
        // Unordered lists
        let inList = false;
        for (let i = 0; i < lines.length; i++) {
            let line = lines[i].trim();
            if (line.startsWith('- ') || line.startsWith('* ')) {
                let content = line.substring(2);
                if (!inList) {
                    lines[i] = '<ul><li>' + content + '</li>';
                    inList = true;
                } else {
                    lines[i] = '<li>' + content + '</li>';
                }
            } else {
                if (inList && !line.startsWith('<li>') && !line.startsWith('<ul>')) {
                    lines[i] = '</ul>' + lines[i];
                    inList = false;
                }
            }
        }
        if (inList) {
            lines[lines.length - 1] += '</ul>';
        }
        
        html = lines.join('\n');

        // Paragraph breaks
        let paragraphs = html.split('\n\n');
        html = paragraphs.map(p => {
            p = p.trim();
            if (!p) return '';
            if (p.startsWith('<h') || p.startsWith('<table') || p.startsWith('<ul') || p.startsWith('<block') || p.startsWith('<div')) {
                return p;
            }
            return `<p>${p.replace(/\n/g, '<br>')}</p>`;
        }).join('');
        
        return html;
    }

    // Resolve date button click
    el.resolveDateBtn.addEventListener("click", () => {
        resolveDate(el.liturgicalDateInput.value);
    });

    // Quick jump date clicks
    el.quickBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetDate = btn.getAttribute("data-date");
            resolveDate(targetDate);
        });
    });

    // Run resolution on load
    initSettings();
    initProfiles();
    initReferencePanel();
    initReferenceResize();
    resolveDate(state.selectedDate);

    /* ==========================================================================
       TAB 2: BOOK BROWSER & KEY INSPECTOR
       ========================================================================== */
    async function loadBooks() {
        el.bookSelect.innerHTML = "<option>Loading books...</option>";
        try {
            const response = await fetch(`${API_BASE}/api/books`);
            if (!response.ok) throw new Error("Failed to fetch books list");
            const data = await response.json();
            
            state.booksData = data;
            
            // Build index mapping key -> file
            state.keyToFileMap = {};
            data.forEach(book => {
                book.keys.forEach(kObj => {
                    state.keyToFileMap[kObj.key] = book.filename;
                });
            });

            // Populate Book Select Dropdown
            let selectHtml = '<option value="">-- Choose a Liturgical Book --</option>';
            data.forEach(book => {
                selectHtml += `<option value="${book.filename}">${book.name} (${book.key_count} keys)</option>`;
            });
            el.bookSelect.innerHTML = selectHtml;

        } catch (err) {
            console.error("Error loading books: ", err);
            el.bookSelect.innerHTML = "<option value=''>Error loading books</option>";
        }
    }

    function renderKeysList() {
        const bookFilename = el.bookSelect.value;
        const searchQuery = el.keySearchInput.value.toLowerCase().trim();
        
        el.keyList.innerHTML = "";
        state.selectedBookFilename = bookFilename;

        if (!bookFilename) {
            el.keyCount.textContent = "0";
            el.keyList.innerHTML = '<li class="placeholder-text" style="padding:20px 0;">Please select a liturgical book above.</li>';
            return;
        }

        const book = state.booksData.find(b => b.filename === bookFilename);
        if (!book) return;

        // Filter keys
        const filteredKeys = book.keys.filter(kObj => {
            const matchesKey = kObj.key.toLowerCase().includes(searchQuery);
            const matchesTitle = kObj.title.toLowerCase().includes(searchQuery);
            const matchesPreview = kObj.preview.toLowerCase().includes(searchQuery);
            return matchesKey || matchesTitle || matchesPreview;
        });

        el.keyCount.textContent = filteredKeys.length;

        if (filteredKeys.length === 0) {
            el.keyList.innerHTML = '<li class="placeholder-text" style="padding:20px 0;">No matching keys found.</li>';
            return;
        }

        let listHtml = "";
        filteredKeys.forEach(kObj => {
            const isActive = state.selectedKey === kObj.key ? "active" : "";
            listHtml += `
                <li class="key-item ${isActive}" data-key="${kObj.key}">
                    <div class="key-item-name">${escapeHtml(kObj.key)}</div>
                    <div class="key-item-preview">${escapeHtml(kObj.preview)}</div>
                </li>
            `;
        });
        el.keyList.innerHTML = listHtml;

        // Attach click listeners to key items
        el.keyList.querySelectorAll(".key-item").forEach(item => {
            item.addEventListener("click", () => {
                const key = item.getAttribute("data-key");
                selectKey(key);
            });
        });
    }

    async function selectKey(key) {
        state.selectedKey = key;
        
        // Highlight active item in sidebar list
        el.keyList.querySelectorAll(".key-item").forEach(item => {
            if (item.getAttribute("data-key") === key) {
                item.classList.add("active");
            } else {
                item.classList.remove("active");
            }
        });

        el.viewerBookBadge.textContent = "Loading...";
        el.viewerKeyId.textContent = key;
        el.diffOriginalContent.innerHTML = '<div class="spinner"></div>';
        el.diffStandardizedContent.innerHTML = '<div class="spinner"></div>';
        
        try {
            const response = await fetch(`${API_BASE}/api/text?key=${key}`);
            if (!response.ok) throw new Error(`HTTP error ${response.status}`);
            const data = await response.json();

            el.viewerBookBadge.textContent = data.filename;
            
            const orig = data.original;
            const std = data.standardized;
            
            state.currentRawKeyData = std;

            // Compute side-by-side diff using word diff helper
            const diffResult = diffWords(orig.content || "", std.content || "");
            
            // Format rubrics display
            const origRubrics = formatRubricsBadge(orig._rubrics);
            const stdRubrics = formatRubricsBadge(std._rubrics);

            el.diffOriginalContent.innerHTML = `
                ${origRubrics}
                ${orig.title ? `<div class="title-medium" style="text-align:left; margin-top:0;">${escapeHtml(orig.title)}</div>` : ""}
                ${orig.verse ? `<div style="font-size:0.95rem; font-style:italic; margin-bottom:12px;">${escapeHtml(orig.verse)}</div>` : ""}
                <div>${diffResult.oldHtml}</div>
                ${orig.source ? `<div style="font-size:0.8rem; color:var(--text-muted); margin-top:16px; font-family:var(--font-ui);">Source: ${escapeHtml(orig.source)}</div>` : ""}
            `;

            el.diffStandardizedContent.innerHTML = `
                ${stdRubrics}
                ${std.title ? `<div class="title-medium" style="text-align:left; margin-top:0;">${escapeHtml(std.title)}</div>` : ""}
                ${std.verse ? `<div style="font-size:0.95rem; font-style:italic; margin-bottom:12px;">${escapeHtml(std.verse)}</div>` : ""}
                <div>${diffResult.newHtml}</div>
                ${std.source ? `<div style="font-size:0.8rem; color:var(--text-muted); margin-top:16px; font-family:var(--font-ui);">Source: ${escapeHtml(std.source)}</div>` : ""}
            `;

            // Setup clean text cache
            state.currentCleanKeyData = std.content || "";

        } catch (err) {
            console.error("Error loading key content: ", err);
            el.diffOriginalContent.innerHTML = `<p class="placeholder-text" style="color:var(--rubric-color);">Failed to load draft content.</p>`;
            el.diffStandardizedContent.innerHTML = `<p class="placeholder-text" style="color:var(--rubric-color);">Failed to load standardized content.</p>`;
            el.viewerBookBadge.textContent = "Error";
        }
    }

    function formatRubricsBadge(rubrics) {
        if (!rubrics || rubrics.length === 0) return "";
        let html = '<div style="margin-bottom: 12px; display:flex; flex-wrap:wrap; gap:6px;">';
        rubrics.forEach(rubric => {
            html += `<span class="badge" style="font-size:0.7rem; border-color:var(--rubric-color); color:var(--rubric-color); background:rgba(144,0,0,0.05); text-transform:none;">${escapeHtml(rubric)}</span>`;
        });
        html += '</div>';
        return html;
    }

    // Select book dropdown change listener
    el.bookSelect.addEventListener("change", () => {
        state.selectedKey = "";
        renderKeysList();
    });

    // Search query key listener with debounce
    let searchTimeout;
    el.keySearchInput.addEventListener("input", () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            renderKeysList();
        }, 300);
    });

    // Copy viewer buttons
    el.copyRawBtn.addEventListener("click", () => {
        if (!state.currentRawKeyData) return;
        const rawJson = JSON.stringify(state.currentRawKeyData, null, 2);
        copyTextToClipboard(rawJson, "Raw JSON object copied!");
    });

    el.copyCleanBtn.addEventListener("click", () => {
        if (!state.currentCleanKeyData) return;
        copyTextToClipboard(state.currentCleanKeyData, "Clean standardized text copied!");
    });

    /* ==========================================================================
       LCS WORD-LEVEL DIFFERENCE ALGORITHM
       ========================================================================== */
    function diffWords(oldStr, newStr) {
        if (!oldStr && !newStr) return { oldHtml: "", newHtml: "" };
        if (!oldStr) return { oldHtml: "", newHtml: `<ins>${escapeHtml(newStr)}</ins>` };
        if (!newStr) return { oldHtml: `<del>${escapeHtml(oldStr)}</del>`, newHtml: "" };

        // Split strings by whitespace tokens, preserving spacing
        const oldWords = oldStr.split(/(\s+)/);
        const newWords = newStr.split(/(\s+)/);

        // DP LCS alignment matrix
        const dp = Array(oldWords.length + 1).fill(null).map(() => Array(newWords.length + 1).fill(0));
        
        for (let i = 1; i <= oldWords.length; i++) {
            for (let j = 1; j <= newWords.length; j++) {
                if (oldWords[i-1] === newWords[j-1]) {
                    dp[i][j] = dp[i-1][j-1] + 1;
                } else {
                    dp[i][j] = Math.max(dp[i-1][j], dp[i][j-1]);
                }
            }
        }

        // Backtrack and compile diff
        let i = oldWords.length;
        let j = newWords.length;
        const diffOld = [];
        const diffNew = [];

        while (i > 0 || j > 0) {
            if (i > 0 && j > 0 && oldWords[i-1] === newWords[j-1]) {
                const escaped = escapeHtml(oldWords[i-1]);
                diffOld.unshift(escaped);
                diffNew.unshift(escaped);
                i--;
                j--;
            } else if (j > 0 && (i === 0 || dp[i][j-1] >= dp[i-1][j])) {
                // Insertions in newWords
                // If it is just whitespace, don't mark as green tags
                const word = newWords[j-1];
                if (word.trim() === "") {
                    diffNew.unshift(escapeHtml(word));
                } else {
                    diffNew.unshift("<ins>" + escapeHtml(word) + "</ins>");
                }
                j--;
            } else if (i > 0 && (j === 0 || dp[i][j-1] < dp[i-1][j])) {
                // Deletions in oldWords
                const word = oldWords[i-1];
                if (word.trim() === "") {
                    diffOld.unshift(escapeHtml(word));
                } else {
                    diffOld.unshift("<del>" + escapeHtml(word) + "</del>");
                }
                i--;
            }
        }

        // Wrap newlines with break elements for proper rendering in diff block
        const cleanOld = diffOld.join('').replace(/\n/g, '<br>');
        const cleanNew = diffNew.join('').replace(/\n/g, '<br>');

        return {
            oldHtml: cleanOld,
            newHtml: cleanNew
        };
    }

    /* ==========================================================================
       TAB 3: LINGUISTIC AUDITOR (LINTER)
       ========================================================================== */
    async function loadLinterReport() {
        el.linterFileList.innerHTML = '<li><div class="spinner"></div></li>';
        el.linterIssueDetails.innerHTML = '<p class="placeholder-text">Loading linter report database...</p>';
        
        try {
            const response = await fetch(`${API_BASE}/api/lint`);
            if (!response.ok) throw new Error("Failed to fetch linter report");
            const data = await response.json();
            
            state.linterReport = data;
            
            // Populate stats row
            el.statTotal.textContent = data.summary.total_issues;
            el.statTerminology.textContent = data.summary.total_terminology_issues;
            el.statPronoun.textContent = data.summary.total_pronoun_issues;
            el.statHieratic.textContent = data.summary.total_hieratic_issues;
            
            renderLinterFileList();

        } catch (err) {
            console.error("Error loading linter report: ", err);
            el.linterFileList.innerHTML = '<li class="placeholder-text" style="color:var(--rubric-color);">Error loading report.</li>';
            el.linterIssueDetails.innerHTML = '<p class="placeholder-text" style="color:var(--rubric-color);">Failed to load linguistic deviations from backend.</p>';
        }
    }

    function renderLinterFileList() {
        let html = "";
        const filesObj = state.linterReport.files;
        
        Object.keys(filesObj).forEach(filename => {
            const fileIssues = filesObj[filename];
            const issueCount = 
                (fileIssues.terminology ? fileIssues.terminology.length : 0) +
                (fileIssues.pronoun ? fileIssues.pronoun.length : 0) +
                (fileIssues.hieratic ? fileIssues.hieratic.length : 0) +
                (fileIssues.typography ? fileIssues.typography.length : 0);
            
            const badgeClass = issueCount > 0 ? "has-errors" : "clean";
            const isActive = state.activeLinterFile === filename ? "active" : "";
            
            html += `
                <li class="linter-file-item ${isActive}" data-file="${filename}">
                    <span class="linter-file-name">${escapeHtml(filename)}</span>
                    <span class="linter-file-badge ${badgeClass}">${issueCount}</span>
                </li>
            `;
        });
        
        el.linterFileList.innerHTML = html;

        // Attach click listeners
        el.linterFileList.querySelectorAll(".linter-file-item").forEach(item => {
            item.addEventListener("click", () => {
                const filename = item.getAttribute("data-file");
                selectLinterFile(filename);
            });
        });
    }

    function selectLinterFile(filename) {
        state.activeLinterFile = filename;
        
        el.linterFileList.querySelectorAll(".linter-file-item").forEach(item => {
            if (item.getAttribute("data-file") === filename) {
                item.classList.add("active");
            } else {
                item.classList.remove("active");
            }
        });

        const fileIssues = state.linterReport.files[filename];
        let html = "";
        let issueIdx = 0;

        // Helper to compile lists of issues
        const addIssues = (issuesArray, type) => {
            if (!issuesArray || issuesArray.length === 0) return;
            
            issuesArray.forEach(issue => {
                issueIdx++;
                
                // Diff details or snippet preview
                let snippetHtml = "";
                if (issue.snippet) {
                    // Highlight the pronoun or match if possible
                    let cleanSnippet = escapeHtml(issue.snippet);
                    if (issue.pronoun) {
                        const reg = new RegExp(`\\b(${issue.pronoun})\\b`, 'gi');
                        cleanSnippet = cleanSnippet.replace(reg, '<del style="text-decoration:none; font-weight:bold;">$1</del>');
                    }
                    snippetHtml = `<div class="issue-ctx-box">${cleanSnippet}</div>`;
                }
                
                html += `
                    <div class="issue-item">
                        <div class="issue-header-row">
                            <span class="issue-key" data-key="${issue.key}" data-file="${filename}">${escapeHtml(issue.key)}</span>
                            <span class="issue-type-badge">${escapeHtml(type)}</span>
                        </div>
                        <div class="issue-description">${escapeHtml(issue.message || "Linguistic deviation detected.")}</div>
                        ${snippetHtml}
                        ${issue.confidence ? `<div style="font-size:0.75rem; color:var(--text-muted); font-style:italic;">Confidence: ${escapeHtml(issue.confidence)}</div>` : ""}
                    </div>
                `;
            });
        };

        addIssues(fileIssues.terminology, "Terminology Drift");
        addIssues(fileIssues.pronoun, "Deity Pronoun");
        addIssues(fileIssues.hieratic, "Holy Object");
        addIssues(fileIssues.typography, "Typography");

        if (issueIdx === 0) {
            el.linterIssueDetails.innerHTML = '<p class="placeholder-text" style="color:var(--status-ok-text);">✓ This database file contains zero deviations! Completely compliant.</p>';
            return;
        }

        el.linterIssueDetails.innerHTML = html;

        // Attach jump to browser clicks
        el.linterIssueDetails.querySelectorAll(".issue-key").forEach(item => {
            item.addEventListener("click", () => {
                const key = item.getAttribute("data-key");
                const file = item.getAttribute("data-file");
                jumpToKeyInBrowser(file, key);
            });
        });
    }

    function jumpToKeyInBrowser(filename, key) {
        // 1. Switch to Browser Tab
        switchTab("tab-browser");
        
        // 2. Select the file/book in dropdown
        el.bookSelect.value = filename;
        state.selectedBookFilename = filename;
        state.selectedKey = key;
        
        // 3. Clear search query to ensure key is visible
        el.keySearchInput.value = "";
        
        // 4. Render key list and select key
        renderKeysList();
        selectKey(key);

        // 5. Scroll key list to show the selected active item
        setTimeout(() => {
            const activeItem = el.keyList.querySelector(".key-item.active");
            if (activeItem) {
                activeItem.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }, 100);
        
        showToast(`Jumped to browser for key: ${key}`);
    }

    /* ==========================================================================
       HTML ESCAPING HELPER
       ========================================================================== */
    function escapeHtml(text) {
        if (!text) return "";
        return text
            .toString()
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function updateRecensionBadge() {
        const badge = document.querySelector(".recension-badge");
        if (!badge) return;
        
        let recensionText = "Stamford Recension";
        if (state.version === "lviv_1899") {
            recensionText = "Lviv Recension";
        } else if (state.version === "st_sergius") {
            recensionText = "St. Sergius Recension";
        }
        badge.textContent = recensionText;
    }

    /* ==========================================================================
       LITURGICAL PARAMETERS SYSTEM
       ========================================================================== */
    function initSettings() {
        // Update badge initially
        updateRecensionBadge();
        const optPaschalionGreg = document.getElementById("opt-paschalion-gregorian");
        const optPaschalionJul = document.getElementById("opt-paschalion-julian");
        const optVersion = document.getElementById("opt-version");
        const optTempleFeast = document.getElementById("opt-temple-feast");
        const optDigestFull = document.getElementById("opt-digest-full");
        const optDigestQuick = document.getElementById("opt-digest-quick");
        const chkDevMode = document.getElementById("chk-dev-mode");
        const optIncludeCeremonial = document.getElementById("opt-include-ceremonial");

        if (state.paschalion === "julian") {
            if (optPaschalionJul) optPaschalionJul.checked = true;
        } else {
            if (optPaschalionGreg) optPaschalionGreg.checked = true;
        }

        if (optVersion) optVersion.value = state.version;
        if (optTempleFeast) optTempleFeast.value = state.templeFeast;

        if (state.digestMode === "quick") {
            if (optDigestQuick) optDigestQuick.checked = true;
        } else {
            if (optDigestFull) optDigestFull.checked = true;
        }

        if (chkDevMode) {
            chkDevMode.checked = state.devMode;
        }
        document.body.classList.toggle("dev-mode-active", state.devMode);

        if (optIncludeCeremonial) {
            optIncludeCeremonial.checked = state.includeCeremonial;
        }

        const saveRadioSetting = (name, stateKey, storageKey) => {
            document.querySelectorAll(`input[name="${name}"]`).forEach(input => {
                input.addEventListener("change", (e) => {
                    state[stateKey] = e.target.value;
                    localStorage.setItem(storageKey, e.target.value);
                    if (state.selectedDate) {
                        resolveDate(state.selectedDate);
                    }
                });
            });
        };

        saveRadioSetting("opt-paschalion", "paschalion", "cantor-opt-paschalion");
        saveRadioSetting("opt-digest-mode", "digestMode", "cantor-opt-digest-mode");

        if (optVersion) {
            optVersion.addEventListener("change", (e) => {
                state.version = e.target.value;
                localStorage.setItem("cantor-opt-version", e.target.value);
                // Dynamically update recension badge
                updateRecensionBadge();
                if (state.selectedDate) {
                    resolveDate(state.selectedDate);
                }
            });
        }

        if (optTempleFeast) {
            optTempleFeast.addEventListener("input", (e) => {
                let val = e.target.value;
                if (val.length === 2 && !val.includes("-") && e.inputType !== "deleteContentBackward") {
                    val = val + "-";
                    optTempleFeast.value = val;
                }
                state.templeFeast = val;
                localStorage.setItem("cantor-opt-temple-feast", val);
                
                if (val.length === 5 || val.length === 0) {
                    if (state.selectedDate) {
                        resolveDate(state.selectedDate);
                    }
                }
            });
        }

        if (optIncludeCeremonial) {
            optIncludeCeremonial.addEventListener("change", (e) => {
                state.includeCeremonial = e.target.checked;
                localStorage.setItem("cantor-opt-include-ceremonial", e.target.checked);
                if (state.selectedDate) {
                    resolveDate(state.selectedDate);
                }
            });
        }

        if (chkDevMode) {
            chkDevMode.addEventListener("change", (e) => {
                state.devMode = e.target.checked;
                localStorage.setItem("cantor-opt-dev-mode", e.target.checked);
                document.body.classList.toggle("dev-mode-active", e.target.checked);
                
                if (!state.devMode && state.activeTab === "linter") {
                    switchTab("tab-calendar");
                }
            });
        }
    }

    /* ==========================================================================
       ROADMAP & HEALTH EXPLORER
       ========================================================================== */
    async function loadRoadmapData() {
        const wingsContainer = document.getElementById("wings-progress-container");
        const matrixContainer = document.getElementById("matrix-grid-container");
        const gatesContainer = document.getElementById("gates-table-body");
        const gapsContainer = document.getElementById("gaps-list-container");
        const timelineContainer = document.getElementById("feast-timeline-container");
        
        if (!wingsContainer || !matrixContainer || !gatesContainer || !gapsContainer || !timelineContainer) {
            return;
        }

        wingsContainer.innerHTML = "<p class='placeholder-text'>Loading wings progress...</p>";
        timelineContainer.innerHTML = "<p class='placeholder-text'>Loading feast timeline...</p>";

        try {
            const currentYear = state.selectedDate ? new Date(state.selectedDate).getFullYear() : new Date().getFullYear();
            const params = new URLSearchParams({
                year: currentYear,
                paschalion: state.paschalion,
                version: state.version,
                temple_feast: state.templeFeast
            });
            const response = await fetch(`${API_BASE}/api/roadmap?${params.toString()}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            state.roadmapData = data;

            wingsContainer.innerHTML = "";
            Object.entries(data.wings).forEach(([wing, percent]) => {
                const wingLabel = wing.charAt(0).toUpperCase() + wing.slice(1);
                wingsContainer.innerHTML += `
                    <div class="wing-progress-item">
                        <div class="wing-progress-label">
                            <span>${wingLabel} Wing</span>
                            <span class="percentage">${percent}%</span>
                        </div>
                        <div class="progress-bar-bg">
                            <div class="progress-bar-fill" style="width: ${percent}%;"></div>
                        </div>
                    </div>
                `;
            });

            matrixContainer.innerHTML = "";
            Object.entries(data.variant_matrix).forEach(([variant, status]) => {
                const prettyName = variant.split("_").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
                let statusClass = "status-incomplete";
                if (status === "completed") statusClass = "status-success";
                else if (status === "stubbed") statusClass = "status-warning";
                
                matrixContainer.innerHTML += `
                    <div class="matrix-card-item ${statusClass}">
                        <div class="matrix-name">${prettyName}</div>
                        <span class="status-badge">${status.toUpperCase()}</span>
                    </div>
                `;
            });

            gatesContainer.innerHTML = "";
            data.matins_gates.forEach(gate => {
                let statusClass = "status-incomplete";
                let icon = "❌";
                if (gate.status === "completed") {
                    statusClass = "gate-success";
                    icon = "✅";
                } else if (gate.status === "stubbed") {
                    statusClass = "gate-warning";
                    icon = "⚠️";
                }
                
                gatesContainer.innerHTML += `
                    <tr class="${statusClass}">
                        <td>Gate ${gate.gate}</td>
                        <td>${gate.name}</td>
                        <td><span class="status-text">${icon} ${gate.status.toUpperCase()}</span></td>
                    </tr>
                `;
            });

            gapsContainer.innerHTML = "";
            data.unresolved_gaps.forEach(gap => {
                gapsContainer.innerHTML += `
                    <div class="gap-item alert-warning">
                        <span class="gap-icon">⚠️</span>
                        <span class="gap-text">${gap}</span>
                    </div>
                `;
            });

            const feastSelect = document.getElementById("feast-cycle-select");
            if (feastSelect) {
                feastSelect.addEventListener("change", () => {
                    state.activeFeastDayIndex = null;
                    renderFeastTimeline();
                });
            }

            renderFeastTimeline();

        } catch (err) {
            console.error("Error loading roadmap: ", err);
            wingsContainer.innerHTML = `<p class="placeholder-text" style="color: var(--rubric-color);">Error loading: ${err.message}</p>`;
        }
    }

    function renderFeastTimeline() {
        const timelineContainer = document.getElementById("feast-timeline-container");
        const detailsPane = document.getElementById("feast-details-pane");
        const feastSelect = document.getElementById("feast-cycle-select");
        
        if (!timelineContainer || !state.roadmapData) return;

        const activeFeastKey = feastSelect ? feastSelect.value : "nativity_theotokos";
        const feastCycle = state.roadmapData.feast_cycles[activeFeastKey];
        if (!feastCycle) return;

        timelineContainer.innerHTML = "";
        feastCycle.days.forEach((day, index) => {
            const isFeast = day.type === "feast";
            const doubleBorderClass = isFeast ? "feast-day" : "";
            const activeClass = state.activeFeastDayIndex === index ? "active" : "";
            
            timelineContainer.innerHTML += `
                <div class="timeline-block ${day.type} ${doubleBorderClass} ${activeClass}" data-index="${index}">
                    <div class="timeline-label">${day.label}</div>
                    <div class="timeline-name-short">${day.name.replace("Nativity of the ", "").replace("Apodosis (Leave-taking) of the ", "").replace("Most Holy ", "")}</div>
                    <div class="timeline-type-badge">${day.type.toUpperCase()}</div>
                </div>
            `;
        });

        document.querySelectorAll(".timeline-block").forEach(block => {
            block.addEventListener("click", () => {
                const index = parseInt(block.getAttribute("data-index"));
                state.activeFeastDayIndex = index;
                renderFeastTimelineDetails(feastCycle.days[index]);
                renderFeastTimeline();
            });
        });

        if (state.activeFeastDayIndex !== null && feastCycle.days[state.activeFeastDayIndex]) {
            renderFeastTimelineDetails(feastCycle.days[state.activeFeastDayIndex]);
        } else {
            detailsPane.innerHTML = `
                <div class="details-placeholder">
                    <span class="timeline-finger-icon">👈</span> Click a timeline block above to inspect fixed vs. relative components.
                </div>
            `;
        }
    }

    function renderFeastTimelineDetails(day) {
        const detailsPane = document.getElementById("feast-details-pane");
        if (!detailsPane) return;

        detailsPane.innerHTML = `
            <div class="feast-details-content glass-container">
                <div class="details-header">
                    <span class="details-badge ${day.type}">${day.type.toUpperCase()}</span>
                    <h4>${day.name}</h4>
                    <div class="details-meta">Date: <strong>${day.date}</strong> | Rank: <strong>${day.rank}</strong> | Tone: <strong>${day.tone_override}</strong></div>
                </div>
                <div class="details-split-view">
                    <div class="details-col fixed-col">
                         <h5>🛡️ Fixed (Festal) Stichera & Canons</h5>
                         <p class="fixed-desc">These texts belong directly to the feast and remain constant throughout the cycle:</p>
                         <div class="fixed-content-box">${day.fixed_text}</div>
                    </div>
                    <div class="details-col relative-col">
                         <h5>🔄 Relative (Weekday/Tone) Variables</h5>
                         <p class="relative-desc">These elements adapt to the specific day of the week, Tone of the week, and other saint intersections:</p>
                         <div class="relative-content-box">${day.relative_rule}</div>
                    </div>
                </div>
                <div class="details-action-row">
                    <button class="btn btn-primary btn-sm" id="btn-feast-jump-resolve" data-date="${day.date}">
                        📅 Resolve Service for ${day.date}
                    </button>
                </div>
            </div>
        `;

        const jumpBtn = document.getElementById("btn-feast-jump-resolve");
        if (jumpBtn) {
            jumpBtn.addEventListener("click", () => {
                const date = jumpBtn.getAttribute("data-date");
                switchTab("tab-calendar");
                resolveDate(date);
            });
        }
    }

    /* ==========================================================================
       IDE-STYLE REFERENCE PANEL LAYOUT SYSTEM
       ========================================================================== */
    function updateReferenceLayout() {
        const mainPanel = document.getElementById("main-document-panel");
        const refPanel = document.getElementById("reference-panel");
        const refResize = document.getElementById("reference-resize");
        const btnToggleRef = document.getElementById("btn-toggle-reference");

        if (!mainPanel || !refPanel || !refResize || !btnToggleRef) return;

        const isOpen = state.referenceOpen;
        localStorage.setItem("cantor-reference-open", isOpen);

        if (isOpen) {
            refPanel.classList.remove("collapsed");
            refResize.style.display = "block";
            btnToggleRef.innerHTML = "📖 Hide Reference Panel";
            btnToggleRef.classList.remove("btn-primary");
            btnToggleRef.classList.add("btn-secondary");

            // Restore width percentage
            const savedPercent = localStorage.getItem("cantor-reference-percent") || "40";
            const percent = parseFloat(savedPercent);
            
            mainPanel.style.width = (100 - percent) + "%";
            mainPanel.style.maxWidth = (100 - percent) + "%";
            refPanel.style.width = percent + "%";
            refPanel.style.maxWidth = percent + "%";
        } else {
            refPanel.classList.add("collapsed");
            refResize.style.display = "none";
            btnToggleRef.innerHTML = "📖 Show Reference Panel";
            btnToggleRef.classList.remove("btn-secondary");
            btnToggleRef.classList.add("btn-primary");

            mainPanel.style.width = "100%";
            mainPanel.style.maxWidth = "100%";
        }
    }

    function initReferencePanel() {
        const btnToggleRef = document.getElementById("btn-toggle-reference");
        const btnCloseRef = document.getElementById("btn-close-reference");
        const refTabs = document.querySelectorAll(".ref-tab-btn");

        if (btnToggleRef) {
            btnToggleRef.addEventListener("click", () => {
                state.referenceOpen = !state.referenceOpen;
                updateReferenceLayout();
            });
        }

        if (btnCloseRef) {
            btnCloseRef.addEventListener("click", () => {
                state.referenceOpen = false;
                updateReferenceLayout();
            });
        }

        // Set up tab switching in the reference panel
        refTabs.forEach(tab => {
            tab.addEventListener("click", () => {
                const targetId = tab.getAttribute("data-ref-target");
                
                // Update tabs active state
                refTabs.forEach(t => t.classList.remove("active"));
                tab.classList.add("active");

                // Toggle visibility of panels inside the reference panel
                const docDigest = document.getElementById("doc-digest");
                const docServiceDigest = document.getElementById("doc-service-digest");

                if (docDigest) docDigest.style.display = targetId === "doc-digest" ? "flex" : "none";
                if (docServiceDigest) docServiceDigest.style.display = targetId === "doc-service-digest" ? "flex" : "none";

                // Save selection
                state.selectedRefTab = targetId;
                localStorage.setItem("cantor-selected-ref-tab", targetId);
            });
        });

        // Initialize active tab from state
        const activeTabBtn = Array.from(refTabs).find(tab => tab.getAttribute("data-ref-target") === state.selectedRefTab);
        if (activeTabBtn) {
            activeTabBtn.click();
        }

        updateReferenceLayout();
    }

    function initReferenceResize() {
        const sidebarResize = document.getElementById("main-sidebar-resize");
        const contextCol = document.querySelector(".context-col");

        const refResize = document.getElementById("reference-resize");
        const contentWrapper = document.querySelector(".document-content-wrapper");
        const mainPanel = document.getElementById("main-document-panel");
        const refPanel = document.getElementById("reference-panel");

        if (!sidebarResize || !contextCol) return;

        // Restore saved sidebar width on load
        const savedSidebarWidth = localStorage.getItem("cantor-sidebar-width");
        if (savedSidebarWidth) {
            contextCol.style.width = savedSidebarWidth + "px";
            contextCol.style.maxWidth = "none";
            contextCol.style.minWidth = "200px";
        }

        // Sidebar dragging
        sidebarResize.addEventListener("mousedown", (e) => {
            e.preventDefault();
            document.body.classList.add("dragging-active");
            sidebarResize.classList.add("dragging");

            const startX = e.clientX;
            const startWidth = contextCol.getBoundingClientRect().width;

            function onMouseMove(moveEvent) {
                const deltaX = moveEvent.clientX - startX;
                let newWidth = startWidth + deltaX;

                if (newWidth < 200) newWidth = 200;
                if (newWidth > 600) newWidth = 600;

                contextCol.style.width = newWidth + "px";
                contextCol.style.maxWidth = "none";
                contextCol.style.minWidth = "200px";
            }

            function onMouseUp() {
                document.body.classList.remove("dragging-active");
                sidebarResize.classList.remove("dragging");
                
                const finalWidth = contextCol.getBoundingClientRect().width;
                localStorage.setItem("cantor-sidebar-width", Math.round(finalWidth));

                document.removeEventListener("mousemove", onMouseMove);
                document.removeEventListener("mouseup", onMouseUp);
            }

            document.addEventListener("mousemove", onMouseMove);
            document.addEventListener("mouseup", onMouseUp);
        });

        // Reference panel dragging
        if (refResize && contentWrapper && mainPanel && refPanel) {
            refResize.addEventListener("mousedown", (e) => {
                if (!state.referenceOpen) return;

                e.preventDefault();
                document.body.classList.add("dragging-active");
                refResize.classList.add("dragging");

                const startX = e.clientX;
                const containerWidth = contentWrapper.getBoundingClientRect().width;
                const startMainWidth = mainPanel.getBoundingClientRect().width;

                function onMouseMove(moveEvent) {
                    const deltaX = moveEvent.clientX - startX;
                    const newMainWidth = startMainWidth + deltaX;
                    
                    let mainPercent = (newMainWidth / containerWidth) * 100;
                    
                    // Constrain reference panel width between 20% and 50% (main panel between 50% and 80%)
                    if (mainPercent < 50) mainPercent = 50;
                    if (mainPercent > 80) mainPercent = 80;

                    const refPercent = 100 - mainPercent;

                    mainPanel.style.width = mainPercent + "%";
                    mainPanel.style.maxWidth = mainPercent + "%";
                    refPanel.style.width = refPercent + "%";
                    refPanel.style.maxWidth = refPercent + "%";
                }

                function onMouseUp() {
                    document.body.classList.remove("dragging-active");
                    refResize.classList.remove("dragging");

                    const finalRefPercent = (refPanel.getBoundingClientRect().width / contentWrapper.getBoundingClientRect().width) * 100;
                    localStorage.setItem("cantor-reference-percent", finalRefPercent.toFixed(2));

                    document.removeEventListener("mousemove", onMouseMove);
                    document.removeEventListener("mouseup", onMouseUp);
                }

                document.addEventListener("mousemove", onMouseMove);
                document.addEventListener("mouseup", onMouseUp);
            });
        }
    }

    /* ==========================================================================
       PARISH PROFILE MANAGER SYSTEM
       ========================================================================== */
    function initProfiles() {
        const optProfile = document.getElementById("opt-profile");
        const btnSaveProfile = document.getElementById("btn-save-profile");
        const btnDeleteProfile = document.getElementById("btn-delete-profile");

        if (!optProfile || !btnSaveProfile || !btnDeleteProfile) return;

        // Render profile select options
        function renderProfileDropdown() {
            optProfile.innerHTML = '<option value="default">Default Profile</option>';
            Object.keys(state.profiles).forEach(pName => {
                const opt = document.createElement("option");
                opt.value = pName;
                opt.textContent = pName;
                optProfile.appendChild(opt);
            });
            optProfile.value = state.activeProfile;
        }

        // Save active settings to a profile
        btnSaveProfile.addEventListener("click", () => {
            const pName = prompt("Enter a name for this Parish Profile (e.g. St. Nicholas - Julian):");
            if (!pName) return;
            const cleanName = pName.trim();
            if (!cleanName || cleanName === "default") {
                showToast("Invalid profile name.");
                return;
            }

            state.profiles[cleanName] = {
                paschalion: state.paschalion,
                version: state.version,
                templeFeast: state.templeFeast,
                digestMode: state.digestMode,
                includeCeremonial: state.includeCeremonial
            };

            localStorage.setItem("cantor-profiles", JSON.stringify(state.profiles));
            state.activeProfile = cleanName;
            localStorage.setItem("cantor-active-profile", cleanName);
            
            renderProfileDropdown();
            showToast(`Profile "${cleanName}" saved successfully!`);
        });

        // Delete profile
        btnDeleteProfile.addEventListener("click", () => {
            if (state.activeProfile === "default") {
                showToast("Cannot delete the Default Profile.");
                return;
            }
            if (!confirm(`Are you sure you want to delete the profile "${state.activeProfile}"?`)) {
                return;
            }

            const oldName = state.activeProfile;
            delete state.profiles[oldName];
            localStorage.setItem("cantor-profiles", JSON.stringify(state.profiles));
            state.activeProfile = "default";
            localStorage.setItem("cantor-active-profile", "default");

            renderProfileDropdown();
            applyProfileSettings("default");
            showToast(`Profile "${oldName}" deleted.`);
        });

        // Swap profile selection
        optProfile.addEventListener("change", (e) => {
            const pName = e.target.value;
            state.activeProfile = pName;
            localStorage.setItem("cantor-active-profile", pName);
            applyProfileSettings(pName);
        });

        // Helper to apply profile configuration to state and inputs
        function applyProfileSettings(pName) {
            let config = {
                paschalion: "gregorian",
                version: "stamford_2014",
                templeFeast: "",
                digestMode: "full",
                includeCeremonial: false
            };

            if (pName !== "default" && state.profiles[pName]) {
                config = state.profiles[pName];
            }

            // Sync state
            state.paschalion = config.paschalion;
            state.version = config.version;
            state.templeFeast = config.templeFeast;
            state.digestMode = config.digestMode;
            state.includeCeremonial = config.includeCeremonial === true;

            // Sync storage
            localStorage.setItem("cantor-opt-paschalion", config.paschalion);
            localStorage.setItem("cantor-opt-version", config.version);
            localStorage.setItem("cantor-opt-temple-feast", config.templeFeast);
            localStorage.setItem("cantor-opt-digest-mode", config.digestMode);
            localStorage.setItem("cantor-opt-include-ceremonial", state.includeCeremonial);

            // Sync UI inputs
            const optPaschalionGreg = document.getElementById("opt-paschalion-gregorian");
            const optPaschalionJul = document.getElementById("opt-paschalion-julian");
            const optVersion = document.getElementById("opt-version");
            const optTempleFeast = document.getElementById("opt-temple-feast");
            const optDigestFull = document.getElementById("opt-digest-full");
            const optDigestQuick = document.getElementById("opt-digest-quick");
            const optIncludeCeremonial = document.getElementById("opt-include-ceremonial");

            if (optPaschalionGreg && optPaschalionJul) {
                if (config.paschalion === "julian") optPaschalionJul.checked = true;
                else optPaschalionGreg.checked = true;
            }
            if (optVersion) optVersion.value = config.version;
            if (optTempleFeast) optTempleFeast.value = config.templeFeast;
            if (optDigestFull && optDigestQuick) {
                if (config.digestMode === "quick") optDigestQuick.checked = true;
                else optDigestFull.checked = true;
            }
            if (optIncludeCeremonial) {
                optIncludeCeremonial.checked = state.includeCeremonial;
            }

            // Update recension badge dynamically
            updateRecensionBadge();

            // Trigger resolve Date if date picked
            if (state.selectedDate) {
                resolveDate(state.selectedDate);
            }
        }

        renderProfileDropdown();
    }

    // Initialize themes
    initTheme();
});
