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
        // Profiles state
        profiles: JSON.parse(localStorage.getItem("cantor-profiles") || "{}"),
        activeProfile: localStorage.getItem("cantor-active-profile") || "default",
        // Split view layout state
        splitView: localStorage.getItem("cantor-opt-split-view") === "true",
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
            }
        });
    });

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
                digest_mode: state.digestMode
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
            "[4 A+G]": "Four-Stichera (with Alleluia & Great Doxology)",
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

    function renderLiturgicalContext(ctx, rubrics, fasting, ceremonial) {
        let html = "";
        
        // General Info
        html += `<div class="context-section-header">Calendar Instance</div>`;
        html += `<div class="context-row"><span class="context-label">Civil Date</span><span class="context-val">${formatHumanDate(ctx.date)}</span></div>`;
        
        const seasonVal = ctx.season || "ordinary";
        const seasonClean = seasonVal.replace('_', ' ');
        html += `<div class="context-row"><span class="context-label">Liturgical Season</span><span class="context-val"><span class="badge-season season-${seasonVal}">${seasonClean}</span></span></div>`;
        
        const toneVal = ctx.tone !== undefined ? `Tone ${ctx.tone}` : "None";
        const toneHtml = ctx.tone !== undefined ? `<span class="badge-tone">${toneVal}</span>` : `<span style="color: var(--text-muted);">None</span>`;
        html += `<div class="context-row"><span class="context-label">Octoechos Tone</span><span class="context-val">${toneHtml}</span></div>`;
        
        const eothVal = ctx.eothinon_number ? `Eothinon ${ctx.eothinon_number}` : "None";
        const eothHtml = ctx.eothinon_number ? `<span class="badge-eothinon">${eothVal}</span>` : `<span style="color: var(--text-muted);">None</span>`;
        html += `<div class="context-row"><span class="context-label">Eothinon Gospel</span><span class="context-val">${eothHtml}</span></div>`;
        
        // Fasting Discipline Row
        html += `<div class="context-row"><span class="context-label">Fasting Discipline</span><span class="context-val">${formatFastingBadge(fasting)}</span></div>`;
        
        // Rank & Commemoration
        html += `<div class="context-section-header">Commemoration & Class</div>`;
        const code = ctx.fixed_rank_code || ctx.dolnytsky_rank_code || "";
        html += `<div class="context-row"><span class="context-label">Rank Code</span><span class="context-val">${translateRankCode(code)}</span></div>`;
        
        const titleVal = cleanLiturgicalText(ctx.dolnytsky_title || "Daily Liturgy");
        html += `<div class="context-row"><span class="context-label">Service Title</span><span class="context-val" style="max-width: 65%; word-break: break-word;">${titleVal}</span></div>`;
        
        const commVal = cleanLiturgicalText(ctx.dolnytsky_commemoration || "None");
        const commHtml = commVal === "None" ? `<span style="color: var(--text-muted);">None</span>` : commVal;
        html += `<div class="context-row"><span class="context-label">Commemoration</span><span class="context-val" style="max-width: 65%; word-break: break-word;">${commHtml}</span></div>`;
        
        // Ceremonial Settings
        if (ceremonial) {
            html += `<div class="context-section-header">Ceremonial Settings</div>`;
            html += `<div class="context-row"><span class="context-label">Liturgical Color</span><span class="context-val">${formatColorBadge(ceremonial.vestment)}</span></div>`;
            html += `<div class="context-row"><span class="context-label">Prostrations</span><span class="context-val">${formatProstrations(ceremonial.prostrations)}</span></div>`;
            const variantLabel = ceremonial.clergy_variant ? ceremonial.clergy_variant.label : "Standard";
            const variantRef = ceremonial.clergy_variant ? `Ordo ${ceremonial.clergy_variant.ordo_ref}` : "";
            html += `<div class="context-row"><span class="context-label">Clergy Variant</span><span class="context-val" style="font-size: 0.85rem;" title="${variantRef}">${variantLabel}</span></div>`;
        }

        // Rubrics Resolution Outputs
        html += `<div class="context-section-header">Rubrics Outcomes</div>`;
        const outlinesVal = formatOutlines(rubrics.overrides.outlines || rubrics.variables.outlines || "Default");
        html += `<div class="context-row"><span class="context-label">Selected Outlines</span><span class="context-val" style="font-family: var(--font-mono); font-size: 0.8rem;">${outlinesVal}</span></div>`;
        
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
            if (isFirstParagraph && !match && !p.startsWith("DATE:") && !p.startsWith("FEAST:")) {
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

    // Markdown-to-HTML parser for Typikon Digest
    function formatMarkdownHtml(mdText) {
        let html = escapeHtml(mdText);
        
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
    initSplitView();
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

    /* ==========================================================================
       LITURGICAL PARAMETERS SYSTEM
       ========================================================================== */
    function initSettings() {
        const optPaschalionGreg = document.getElementById("opt-paschalion-gregorian");
        const optPaschalionJul = document.getElementById("opt-paschalion-julian");
        const optVersion = document.getElementById("opt-version");
        const optTempleFeast = document.getElementById("opt-temple-feast");
        const optDigestFull = document.getElementById("opt-digest-full");
        const optDigestQuick = document.getElementById("opt-digest-quick");
        const chkDevMode = document.getElementById("chk-dev-mode");

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
       SPLIT VIEW LAYOUT SYSTEM
       ========================================================================== */
    function initSplitView() {
        const btnToggleLayout = document.getElementById("btn-toggle-layout");
        const docCard = document.querySelector(".document-card");

        if (!btnToggleLayout || !docCard) return;

        // Apply initial state
        if (state.splitView) {
            docCard.classList.add("split-layout-active");
            btnToggleLayout.innerHTML = "📖 Tabbed View";
        } else {
            docCard.classList.remove("split-layout-active");
            btnToggleLayout.innerHTML = "📖 Split View";
        }

        btnToggleLayout.addEventListener("click", () => {
            state.splitView = !state.splitView;
            localStorage.setItem("cantor-opt-split-view", state.splitView);
            
            if (state.splitView) {
                docCard.classList.add("split-layout-active");
                btnToggleLayout.innerHTML = "📖 Tabbed View";
                showToast("Split view enabled (Booklet & Digest side-by-side)");
            } else {
                docCard.classList.remove("split-layout-active");
                btnToggleLayout.innerHTML = "📖 Split View";
                showToast("Tabbed view enabled");
            }
        });
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
                digestMode: state.digestMode
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
                digestMode: "full"
            };

            if (pName !== "default" && state.profiles[pName]) {
                config = state.profiles[pName];
            }

            // Sync state
            state.paschalion = config.paschalion;
            state.version = config.version;
            state.templeFeast = config.templeFeast;
            state.digestMode = config.digestMode;

            // Sync storage
            localStorage.setItem("cantor-opt-paschalion", config.paschalion);
            localStorage.setItem("cantor-opt-version", config.version);
            localStorage.setItem("cantor-opt-temple-feast", config.templeFeast);
            localStorage.setItem("cantor-opt-digest-mode", config.digestMode);

            // Sync UI inputs
            const optPaschalionGreg = document.getElementById("opt-paschalion-gregorian");
            const optPaschalionJul = document.getElementById("opt-paschalion-julian");
            const optVersion = document.getElementById("opt-version");
            const optTempleFeast = document.getElementById("opt-temple-feast");
            const optDigestFull = document.getElementById("opt-digest-full");
            const optDigestQuick = document.getElementById("opt-digest-quick");

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
