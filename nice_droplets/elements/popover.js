export default {
    template: `
    <teleport to="body">
        <div
          class="suggestionView"
          :style="style"
          ref="dockView"
        >
      <slot />
      </div>
    </teleport>`,
    data() {
        return {
            listeners: {},
        }
    },
    props: {
        showEvents: Array,
        hideEvents: Array,
    },
    mounted() {
        // Start hidden, but ensure pointerEvents & z-index remain on the element
        this.$refs.dockView.style = "display:none; position:absolute;";
        this.$refs.dockView.style.pointerEvents = "auto";
        this.$refs.dockView.style.zIndex = 2147483647; // a very large z-index

        // Prevent click events from propagating
        this.$refs.dockView.addEventListener('mousedown', event => {
            event.preventDefault();
            event.stopPropagation();
        });
        this.$refs.dockView.addEventListener('click', event => {
            event.preventDefault();
            event.stopPropagation();
        });
    },
    beforeUnmount() {
        this._detachAllElements()
    },
    methods: {
        moveToElement(target) {
            const targetRect = target.getBoundingClientRect();
            let top = targetRect.bottom + window.scrollY;
            let left = targetRect.left + window.scrollX;

            requestAnimationFrame(() => {
                const viewRect = this.$refs.dockView.getBoundingClientRect();
                const viewHeight = viewRect.height;
                if ( // if not enough space below, move up
                    targetRect.bottom + viewHeight > window.innerHeight &&
                    targetRect.top - viewHeight > 0
                ) {
                    this.$refs.dockView.style.transform = "translateY(-100%)";
                    top = targetRect.top + window.scrollY;
                } else {
                    this.$refs.dockView.style.transform = "translateY(0)";
                }
                // Update the absolute positioning
                this.$refs.dockView.style = `position:absolute; top:${top}px; left:${left}px;`;
            });
        },
        attachElement(elementId) {
            const element = getHtmlElement(elementId)
            if (!element) {
                console.warn("Could not attach DockingView to element with id ${elementId}.");
                return;
            }
            const showHandler = () => this.show_at(elementId);
            const hideHandler = () => this.hide();
            let listenerDict = {};
            for (const eventName of this.showEvents || []) {
                element.addEventListener(eventName, showHandler);
                listenerDict[eventName] = showHandler;
            }
            for (const eventName of this.hideEvents || []) {
                element.addEventListener(eventName, hideHandler);
                listenerDict[eventName] = hideHandler;
            }
            this.listeners[elementId] = listenerDict;
        },
        detachElement(elementId) {
            const element = getHtmlElement(elementId)
            if (!element) {
                return;
            }
            const handlers = this.listeners[elementId];
            if (handlers) {
                for (const eventName in handlers) {
                    element.removeEventListener(eventName, handlers[eventName]);
                }
                delete this.listeners[elementId];
            }
        },
        show_at(elementId) {
            const targetElement = getHtmlElement(elementId)
            if (!targetElement) {
                console.warn("Could not show DockingView at element with id ${elementId}.");
                return;
            }
            this._setVisible()
            this.moveToElement(targetElement);
            // find element id
            this.$emit('_show', {
                target: elementId
            })
        },
        hide(element) {
            this._setVisible(false)
            this.$emit('_hide', {})
        },
        _setVisible(visible = true) {
            this.$refs.dockView.style = visible ? "display:flex;" : "display:none;"
        },
        _detachAllElements() {
            Object.keys(this.listeners).forEach(key => this.detachElement(key))
        }
    }
};