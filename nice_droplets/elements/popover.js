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
            observer: null,
            _currentTarget: null
        }
    },
    props: {
        showEvents: Array,
        hideEvents: Array,
        dockingSide: String,
    },
    mounted() {
        this.$refs.dockView.style.visibility = 'hidden';
        this.$refs.dockView.style.position = 'absolute';
        this.$refs.dockView.style.pointerEvents = "auto";
        this.$refs.dockView.style.zIndex = 2147483647;

        this.$refs.dockView.addEventListener('mousedown', event => {
            event.preventDefault();
            event.stopPropagation();
        });
        this.$refs.dockView.addEventListener('click', event => {
            event.preventDefault();
            event.stopPropagation();
        });

        this.observer = new MutationObserver(() => {
            if (this._currentTarget) {
                this.moveToElement(this._currentTarget);
            }
        });

        this.observer.observe(this.$refs.dockView, {
            childList: true,
            subtree: true,
            characterData: true,
            attributes: true
        });
    },
    beforeUnmount() {
        if (this.observer) {
            this.observer.disconnect();
        }
        this._detachAllElements()
    },
    methods: {
        moveToElement(target) {
            if (this.$refs.dockView.style.visibility === 'hidden') {
                return;
            }
            this._currentTarget = target;
            const targetRect = target.getBoundingClientRect();
            let top = targetRect.bottom + window.scrollY;
            let left = targetRect.left + window.scrollX;

            const dockingSide = this.dockingSide;

            requestAnimationFrame(() => {
                const viewRect = this.$refs.dockView.getBoundingClientRect();
                const viewHeight = viewRect.height;
                const viewWidth = viewRect.width;
                const targetWidth = targetRect.width;
                this.$refs.dockView.style.width = `${targetWidth}px`;

                const components = dockingSide.split(' ');

                let vertical = components.find(c => c === 'top' || c === 'bottom');
                let horizontal = components.find(c => c === 'left' || c === 'right');

                const firstComponent = components[0];
                const isHorizontalFirst = firstComponent === 'left' || firstComponent === 'right';

                if (isHorizontalFirst) {
                    if (vertical === 'bottom' && targetRect.bottom - viewHeight < 0) {
                        vertical = 'top';
                    }
                    if (horizontal === 'left') {
                        left = targetRect.left + window.scrollX - viewWidth;
                    } else if (horizontal === 'right') {
                        left = targetRect.right + window.scrollX;
                    }
                    if (vertical === 'top') {
                        top = targetRect.top + window.scrollY;
                    } else if (vertical === 'bottom') {
                        top = targetRect.bottom + window.scrollY - viewHeight;
                    } else {
                        top = targetRect.top + window.scrollY;
                        this.$refs.dockView.style.height = `${targetRect.height}px`;
                    }
                } else {
                    if (vertical === 'top' && targetRect.top - viewHeight < 0) {
                        vertical = 'bottom';
                    }
                    if (vertical === 'top') {
                        top = targetRect.top + window.scrollY - viewHeight;
                        if (!horizontal) {
                            this.$refs.dockView.style.width = `${targetRect.width}px`;
                        }
                    } else if (vertical === 'bottom') {
                        top = targetRect.bottom + window.scrollY;
                        if (!horizontal) {
                            this.$refs.dockView.style.width = `${targetRect.width}px`;
                        }
                    }
                    if (horizontal === 'left') {
                        left = targetRect.left + window.scrollX;
                    } else if (horizontal === 'right') {
                        left = targetRect.right + window.scrollX - viewWidth;
                    } else {
                        left = targetRect.left + window.scrollX;
                    }
                }
                if (left < 0) {
                    left = 0;
                }            
                if (top < 0) {
                    top = 0;
                }            
                this.$refs.dockView.style.top = `${top}px`;
                this.$refs.dockView.style.left = `${left}px`;
                this.$refs.dockView.style.position = 'absolute';
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
            this.$emit('_show', {
                target: elementId
            })
        },
        hide(element) {
            this._setVisible(false)
            this.$emit('_hide', {})
        },
        _setVisible(visible = true) {
            this.$refs.dockView.style.visibility = visible ? "visible" : "hidden";
        },
        _detachAllElements() {
            Object.keys(this.listeners).forEach(key => this.detachElement(key))
        }
    }
};