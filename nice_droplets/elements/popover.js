export default {
    template: `
        <div
          class="ndPopover"
          :style="style"
          ref="dockView"
        >
      <slot />
      </div>
    `,
    data() {
        return {
            listeners: {},
            observer: null,
            _currentTarget: null,
            _keepHidden: False
        }
    },
    props: {
        showEvents: Array,
        hideEvents: Array,
        offsets: String,
        dockingSide: String,
    },
    mounted() {
        this.$refs.dockView.style.visibility = 'hidden';
        this.$refs.dockView.style.position = 'fixed';
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
            let top = targetRect.bottom;
            let left = targetRect.left;

            const dockingSide = this.dockingSide;
            // convert offset to string to efficient offsets in pixels, it can be one, two or four values
            let efficient_offsets = [0, 0, 0, 0];                            
            if (this.offsets) {
                const offsets = this.offsets.split(' ');
                if (offsets.length === 1) {
                    efficient_offsets = [Number(offsets[0]), Number(offsets[0]), Number(offsets[0]), Number(offsets[0])];
                } else if (offsets.length === 2) {
                    efficient_offsets = [Number(offsets[0]), Number(offsets[1]), Number(offsets[0]), Number(offsets[1])];
                } else {
                    efficient_offsets = [Number(offsets[0]), Number(offsets[1]), Number(offsets[2]), Number(offsets[3])];
                }
            }

            requestAnimationFrame(() => {
                const viewRect = this.$refs.dockView.getBoundingClientRect();
                const viewHeight = viewRect.height;
                const viewWidth = viewRect.width;
                const targetWidth = targetRect.width;

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
                        left = targetRect.left - viewWidth;
                    } else if (horizontal === 'right') {
                        left = targetRect.right;
                    }
                    if (vertical === 'top') {
                        top = targetRect.top;
                    } else if (vertical === 'bottom') {
                        top = targetRect.bottom - viewHeight;
                    } else {
                        top = targetRect.top;
                        this.$refs.dockView.style.height = `${targetRect.height}px`;
                    }
                } else {
                    if (vertical === 'top' && targetRect.top - viewHeight < 0) {
                        vertical = 'bottom';
                    }
                    if (vertical === 'top') {
                        top = targetRect.top - viewHeight;
                        if (!horizontal) {
                            this.$refs.dockView.style.width = `${targetRect.width}px`;
                        }
                    } else if (vertical === 'bottom') {
                        top = targetRect.bottom;
                        if (!horizontal) {
                            this.$refs.dockView.style.width = `${targetRect.width}px`;
                        }
                    }
                    if (horizontal === 'left') {
                        left = targetRect.left;
                    } else if (horizontal === 'right') {
                        left = targetRect.right - viewWidth;
                    } else {
                        left = targetRect.left;
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
            });
        },
        attachElement(elementId) {
            const element = getHtmlElement(elementId)
            if (!element) {
                console.warn("Could not attach DockingView to element with id ${elementId}.");
                return;
            }
            const showHandler = () => this.showAt(elementId);
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
        showAt(elementId) {
            const targetElement = getHtmlElement(elementId)
            if (!targetElement) {
                console.warn("Could not show DockingView at element with id ${elementId}.");
                return;
            }
            if (!this._keepHidden) {
                this._setVisible()
            }
            this._currentTarget = targetElement
            this.moveToElement(targetElement);
            this.$emit('_show', {
                target: elementId
            })
        },
        hide() {
            this._setVisible(false)
            this._currentTarget = null
            this.$emit('_hide', {})
        },
        setKeepHidden(keepHidden) {
            this._keepHidden = keepHidden
            if(keepHidden) {
                this._setVisible(false)
            } else if(this._currentTarget) {
                this._setVisible(true)
                this.moveToElement(this._currentTarget);
            }
        },
        _setVisible(visible = true) {
            this.$refs.dockView.style.visibility = visible ? "visible" : "hidden";
        },
        _detachAllElements() {
            Object.keys(this.listeners).forEach(key => this.detachElement(key))
        }
    }
};