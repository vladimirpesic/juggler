<!--
  Vue Language Test File
  Tests all structural elements supported by the Vue parser
-->

<template>
  <!-- Template with all Vue directives and features -->
  <div class="test-component" :class="{ active: isActive, disabled: !isEnabled }">
    <!-- Conditional rendering -->
    <div v-if="showHeader" class="header">
      <h1>{{ title }}</h1>
      <h2 v-show="showSubtitle">{{ subtitle }}</h2>
    </div>

    <!-- Template references -->
    <input 
      ref="inputRef"
      v-model="inputValue"
      :placeholder="inputPlaceholder"
      @input="handleInput"
      @focus="handleFocus"
      @blur="handleBlur"
    />

    <!-- List rendering with key -->
    <ul v-if="items.length > 0">
      <li 
        v-for="(item, index) in filteredItems" 
        :key="item.id"
        :class="{ selected: selectedItem === item.id }"
        @click="selectItem(item)"
      >
        <span>{{ index + 1 }}. {{ item.name }}</span>
        <span class="priority" :class="`priority-${item.priority}`">
          {{ item.priority }}
        </span>
        <button @click.stop="removeItem(item.id)">Remove</button>
      </li>
    </ul>
    <div v-else class="empty-state">
      <p>No items to display</p>
    </div>

    <!-- Form handling -->
    <form @submit.prevent="submitForm" class="form">
      <div class="form-group">
        <label for="name">Name:</label>
        <input 
          id="name"
          v-model.trim="form.name"
          type="text"
          required
        />
      </div>

      <div class="form-group">
        <label for="email">Email:</label>
        <input 
          id="email"
          v-model="form.email"
          type="email"
          :class="{ invalid: !isValidEmail }"
        />
      </div>

      <div class="form-group">
        <label for="age">Age:</label>
        <input 
          id="age"
          v-model.number="form.age"
          type="number"
          min="0"
          max="150"
        />
      </div>

      <div class="form-group">
        <label for="bio">Bio:</label>
        <textarea 
          id="bio"
          v-model="form.bio"
          rows="4"
          :maxlength="bioMaxLength"
        ></textarea>
        <small>{{ form.bio.length }}/{{ bioMaxLength }}</small>
      </div>

      <div class="form-group">
        <label>
          <input 
            v-model="form.newsletter"
            type="checkbox"
          />
          Subscribe to newsletter
        </label>
      </div>

      <div class="form-group">
        <label>Gender:</label>
        <label>
          <input 
            v-model="form.gender"
            type="radio"
            value="male"
          />
          Male
        </label>
        <label>
          <input 
            v-model="form.gender"
            type="radio" 
            value="female"
          />
          Female
        </label>
        <label>
          <input 
            v-model="form.gender"
            type="radio"
            value="other"
          />
          Other
        </label>
      </div>

      <div class="form-group">
        <label for="country">Country:</label>
        <select id="country" v-model="form.country">
          <option value="">Select country</option>
          <option 
            v-for="country in countries" 
            :key="country.code"
            :value="country.code"
          >
            {{ country.name }}
          </option>
        </select>
      </div>

      <div class="form-group">
        <label for="skills">Skills:</label>
        <select id="skills" v-model="form.skills" multiple>
          <option 
            v-for="skill in availableSkills"
            :key="skill"
            :value="skill"
          >
            {{ skill }}
          </option>
        </select>
      </div>

      <button type="submit" :disabled="!isFormValid">Submit</button>
      <button type="button" @click="resetForm">Reset</button>
    </form>

    <!-- Custom directives -->
    <div v-focus class="custom-directive-test">
      <p v-highlight="'yellow'">This text should be highlighted</p>
      <p v-tooltip="'This is a tooltip'">Hover for tooltip</p>
    </div>

    <!-- Slots and component composition -->
    <card-component 
      :title="cardTitle"
      :loading="isLoading"
      @update="handleCardUpdate"
    >
      <template #header>
        <h3>Custom Header Content</h3>
      </template>

      <p>Default slot content</p>
      <button @click="toggleLoading">Toggle Loading</button>

      <template #footer>
        <small>Last updated: {{ lastUpdated }}</small>
      </template>
    </card-component>

    <!-- Dynamic components -->
    <component 
      :is="currentComponent"
      v-bind="componentProps"
      @component-event="handleComponentEvent"
    ></component>

    <!-- Transition and animation -->
    <transition name="fade" mode="out-in">
      <div v-if="showTransitionContent" key="content" class="transition-content">
        <p>This content has transitions</p>
      </div>
      <div v-else key="loading" class="loading">
        <p>Loading...</p>
      </div>
    </transition>

    <transition-group name="list" tag="div" class="list-container">
      <div 
        v-for="item in animatedItems"
        :key="item.id"
        class="list-item"
      >
        {{ item.text }}
      </div>
    </transition-group>

    <!-- Event modifiers -->
    <div class="event-modifiers">
      <button @click.once="handleOnceClick">Click Once</button>
      <button @click.prevent="handlePreventDefault">Prevent Default</button>
      <button @click.stop="handleStopPropagation">Stop Propagation</button>
      <div @click="handleParentClick">
        <button @click.stop="handleChildClick">Child (stop propagation)</button>
      </div>
    </div>

    <!-- Key modifiers -->
    <input 
      @keyup.enter="handleEnterKey"
      @keyup.esc="handleEscapeKey"
      @keyup.ctrl.s="handleCtrlS"
      placeholder="Try Enter, Esc, or Ctrl+S"
    />

    <!-- Async components and Suspense (Vue 3) -->
    <Suspense>
      <template #default>
        <async-component :data="asyncData" />
      </template>
      <template #fallback>
        <div>Loading async component...</div>
      </template>
    </Suspense>

    <!-- Teleport (Vue 3) -->
    <teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click="closeModal">
        <div class="modal" @click.stop>
          <h3>Modal Title</h3>
          <p>Modal content</p>
          <button @click="closeModal">Close</button>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script>
// Options API (Vue 2 style)
import { defineComponent } from 'vue'
import CardComponent from './components/CardComponent.vue'
import AsyncComponent from './components/AsyncComponent.vue'

export default defineComponent({
  name: 'TestComponent',
  
  // Component registration
  components: {
    CardComponent,
    AsyncComponent
  },

  // Props definition
  props: {
    title: {
      type: String,
      required: true,
      default: 'Default Title'
    },
    subtitle: {
      type: String,
      default: ''
    },
    initialItems: {
      type: Array,
      default: () => []
    },
    config: {
      type: Object,
      default: () => ({
        theme: 'light',
        locale: 'en'
      }),
      validator(value) {
        return value && typeof value === 'object'
      }
    },
    maxItems: {
      type: Number,
      default: 100,
      validator(value) {
        return value > 0 && value <= 1000
      }
    }
  },

  // Emits declaration (Vue 3)
  emits: {
    'item-selected': (item) => {
      return item && typeof item === 'object' && item.id
    },
    'form-submitted': (formData) => {
      return formData && typeof formData === 'object'
    },
    'update:modelValue': (value) => true,
    'custom-event': null
  },

  // Data properties
  data() {
    return {
      // Reactive data
      isActive: false,
      isEnabled: true,
      showHeader: true,
      showSubtitle: false,
      inputValue: '',
      inputPlaceholder: 'Enter some text...',
      selectedItem: null,
      isLoading: false,
      showTransitionContent: true,
      showModal: false,
      lastUpdated: new Date().toISOString(),
      
      // Form data
      form: {
        name: '',
        email: '',
        age: null,
        bio: '',
        newsletter: false,
        gender: '',
        country: '',
        skills: []
      },
      
      // Lists and objects
      items: [
        { id: 1, name: 'Item 1', priority: 'high', category: 'work' },
        { id: 2, name: 'Item 2', priority: 'medium', category: 'personal' },
        { id: 3, name: 'Item 3', priority: 'low', category: 'work' },
        { id: 4, name: 'Item 4', priority: 'high', category: 'personal' }
      ],
      
      animatedItems: [
        { id: 1, text: 'Animated Item 1' },
        { id: 2, text: 'Animated Item 2' },
        { id: 3, text: 'Animated Item 3' }
      ],
      
      countries: [
        { code: 'us', name: 'United States' },
        { code: 'ca', name: 'Canada' },
        { code: 'uk', name: 'United Kingdom' },
        { code: 'de', name: 'Germany' },
        { code: 'fr', name: 'France' }
      ],
      
      availableSkills: [
        'JavaScript',
        'Vue.js',
        'React',
        'Angular',
        'Node.js',
        'Python',
        'TypeScript',
        'CSS',
        'HTML'
      ],
      
      // Component state
      currentComponent: 'div',
      componentProps: {},
      asyncData: null,
      
      // Constants
      bioMaxLength: 500
    }
  },

  // Computed properties
  computed: {
    // Simple computed property
    filteredItems() {
      return this.items.filter(item => 
        item.name.toLowerCase().includes(this.inputValue.toLowerCase())
      )
    },

    // Computed property with getter and setter
    cardTitle: {
      get() {
        return `${this.title} - ${this.items.length} items`
      },
      set(value) {
        this.$emit('update:title', value)
      }
    },

    // Complex computed property
    isFormValid() {
      return this.form.name.length > 0 &&
             this.form.email.length > 0 &&
             this.isValidEmail &&
             this.form.age !== null &&
             this.form.age >= 0
    },

    isValidEmail() {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return emailRegex.test(this.form.email)
    },

    // Computed property using other computed properties
    itemStats() {
      const stats = {
        total: this.items.length,
        high: 0,
        medium: 0,
        low: 0
      }
      
      this.items.forEach(item => {
        stats[item.priority]++
      })
      
      return stats
    },

    // Computed property with parameters (using closure)
    getItemsByCategory() {
      return (category) => {
        return this.items.filter(item => item.category === category)
      }
    }
  },

  // Watchers
  watch: {
    // Simple watcher
    inputValue(newValue, oldValue) {
      console.log(`Input changed from "${oldValue}" to "${newValue}"`)
    },

    // Deep watcher
    form: {
      handler(newForm, oldForm) {
        console.log('Form data changed:', newForm)
        this.lastUpdated = new Date().toISOString()
      },
      deep: true
    },

    // Immediate watcher
    items: {
      handler(newItems) {
        this.$emit('items-changed', newItems)
      },
      immediate: true
    },

    // Watcher with string method name
    selectedItem: 'onSelectedItemChange',

    // Multiple watchers for the same property
    isLoading: [
      function(val) {
        console.log('Loading state changed:', val)
      },
      {
        handler: 'onLoadingChange',
        immediate: true
      }
    ]
  },

  // Lifecycle hooks
  beforeCreate() {
    console.log('beforeCreate: Component instance is about to be created')
  },

  created() {
    console.log('created: Component instance has been created')
    this.initializeComponent()
  },

  beforeMount() {
    console.log('beforeMount: Component is about to be mounted')
  },

  mounted() {
    console.log('mounted: Component has been mounted to the DOM')
    this.setupEventListeners()
    this.$nextTick(() => {
      console.log('DOM fully updated after mount')
    })
  },

  beforeUpdate() {
    console.log('beforeUpdate: Component is about to update')
  },

  updated() {
    console.log('updated: Component has been updated')
  },

  beforeUnmount() {
    console.log('beforeUnmount: Component is about to be unmounted')
    this.cleanup()
  },

  unmounted() {
    console.log('unmounted: Component has been unmounted')
  },

  // Error handling
  errorCaptured(err, instance, info) {
    console.error('Error captured:', err, info)
    return false
  },

  // Methods
  methods: {
    // Event handlers
    handleInput(event) {
      console.log('Input event:', event.target.value)
    },

    handleFocus(event) {
      console.log('Input focused')
      event.target.classList.add('focused')
    },

    handleBlur(event) {
      console.log('Input blurred')
      event.target.classList.remove('focused')
    },

    selectItem(item) {
      this.selectedItem = item.id
      this.$emit('item-selected', item)
    },

    removeItem(itemId) {
      const index = this.items.findIndex(item => item.id === itemId)
      if (index > -1) {
        this.items.splice(index, 1)
      }
    },

    // Form methods
    submitForm() {
      if (this.isFormValid) {
        const formData = { ...this.form }
        console.log('Submitting form:', formData)
        this.$emit('form-submitted', formData)
        
        // Simulate API call
        this.isLoading = true
        setTimeout(() => {
          this.isLoading = false
          alert('Form submitted successfully!')
        }, 2000)
      }
    },

    resetForm() {
      this.form = {
        name: '',
        email: '',
        age: null,
        bio: '',
        newsletter: false,
        gender: '',
        country: '',
        skills: []
      }
    },

    // Component methods
    toggleLoading() {
      this.isLoading = !this.isLoading
    },

    handleCardUpdate(data) {
      console.log('Card updated:', data)
    },

    handleComponentEvent(payload) {
      console.log('Component event received:', payload)
    },

    // Event modifier handlers
    handleOnceClick() {
      console.log('This will only be called once')
    },

    handlePreventDefault(event) {
      console.log('Default behavior prevented')
    },

    handleStopPropagation(event) {
      console.log('Event propagation stopped')
    },

    handleParentClick() {
      console.log('Parent clicked')
    },

    handleChildClick() {
      console.log('Child clicked')
    },

    // Key event handlers
    handleEnterKey() {
      console.log('Enter key pressed')
    },

    handleEscapeKey() {
      console.log('Escape key pressed')
    },

    handleCtrlS(event) {
      console.log('Ctrl+S pressed')
    },

    // Modal methods
    closeModal() {
      this.showModal = false
    },

    // Watcher callback methods
    onSelectedItemChange(newItem, oldItem) {
      console.log(`Selected item changed from ${oldItem} to ${newItem}`)
    },

    onLoadingChange(isLoading) {
      if (isLoading) {
        document.body.classList.add('loading')
      } else {
        document.body.classList.remove('loading')
      }
    },

    // Utility methods
    initializeComponent() {
      console.log('Initializing component with props:', this.$props)
      this.items = [...this.initialItems, ...this.items]
    },

    setupEventListeners() {
      window.addEventListener('resize', this.handleWindowResize)
    },

    cleanup() {
      window.removeEventListener('resize', this.handleWindowResize)
    },

    handleWindowResize() {
      console.log('Window resized')
    },

    // Async method
    async loadAsyncData() {
      try {
        this.isLoading = true
        const response = await fetch('/api/data')
        const data = await response.json()
        this.asyncData = data
      } catch (error) {
        console.error('Failed to load async data:', error)
      } finally {
        this.isLoading = false
      }
    },

    // Method with parameter destructuring
    updateItem({ id, ...updates }) {
      const index = this.items.findIndex(item => item.id === id)
      if (index > -1) {
        this.items[index] = { ...this.items[index], ...updates }
      }
    },

    // Method using template refs
    focusInput() {
      this.$refs.inputRef?.focus()
    }
  },

  // Provide/Inject
  provide() {
    return {
      testComponentInstance: this,
      theme: this.config.theme,
      updateTheme: this.updateTheme
    }
  },

  // Custom options
  customOption: 'This is a custom option',

  // Mixins (if any)
  // mixins: [SomeMixin],

  // Directives
  directives: {
    // Custom directive
    focus: {
      mounted(el) {
        el.focus()
      }
    },
    
    // Directive with parameters
    highlight: {
      mounted(el, binding) {
        el.style.backgroundColor = binding.value || 'yellow'
      },
      updated(el, binding) {
        el.style.backgroundColor = binding.value || 'yellow'
      }
    },
    
    // Complex directive with all hooks
    tooltip: {
      beforeMount(el, binding) {
        // Setup
      },
      mounted(el, binding) {
        el.setAttribute('title', binding.value)
      },
      beforeUpdate(el, binding) {
        // Before update
      },
      updated(el, binding) {
        el.setAttribute('title', binding.value)
      },
      beforeUnmount(el) {
        // Cleanup before unmount
      },
      unmounted(el) {
        // Cleanup after unmount
      }
    }
  }
})
</script>

<script setup>
// Composition API (Vue 3 style) - alternative to Options API
// This would be in a separate component or replace the Options API above

/*
import { ref, reactive, computed, watch, onMounted, onUnmounted, provide, inject } from 'vue'

// Props
const props = defineProps({
  title: String,
  initialData: Array
})

// Emits
const emit = defineEmits(['update', 'change'])

// Reactive data
const count = ref(0)
const state = reactive({
  items: [],
  loading: false
})

// Computed
const doubledCount = computed(() => count.value * 2)

// Watchers
watch(count, (newCount, oldCount) => {
  console.log(`Count changed from ${oldCount} to ${newCount}`)
})

// Lifecycle
onMounted(() => {
  console.log('Component mounted')
})

onUnmounted(() => {
  console.log('Component unmounted')
})

// Methods
function increment() {
  count.value++
}

function handleUpdate() {
  emit('update', { count: count.value })
}

// Provide
provide('count', count)

// Expose to template
defineExpose({
  increment,
  count
})
*/
</script>

<style scoped>
/* Scoped styles */
.test-component {
  padding: 20px;
  font-family: Arial, sans-serif;
}

.test-component.active {
  border: 2px solid #007bff;
}

.test-component.disabled {
  opacity: 0.5;
  pointer-events: none;
}

.header {
  margin-bottom: 20px;
}

.header h1 {
  color: #333;
  font-size: 2rem;
}

.form {
  max-width: 500px;
  margin: 20px 0;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.form-group input.invalid {
  border-color: #dc3545;
}

.form-group input[type="radio"],
.form-group input[type="checkbox"] {
  width: auto;
  margin-right: 5px;
}

.priority {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  text-transform: uppercase;
}

.priority-high {
  background-color: #dc3545;
  color: white;
}

.priority-medium {
  background-color: #ffc107;
  color: black;
}

.priority-low {
  background-color: #28a745;
  color: white;
}

.empty-state {
  text-align: center;
  color: #666;
  font-style: italic;
  padding: 40px;
}

.event-modifiers {
  margin: 20px 0;
}

.event-modifiers button {
  margin-right: 10px;
  margin-bottom: 10px;
}

/* Transition styles */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.list-move {
  transition: transform 0.3s ease;
}

.transition-content,
.loading {
  padding: 20px;
  text-align: center;
}

.list-container {
  margin: 20px 0;
}

.list-item {
  padding: 10px;
  margin: 5px 0;
  background-color: #f8f9fa;
  border-radius: 4px;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  max-width: 500px;
  width: 90%;
}

/* Custom directive styles */
.custom-directive-test {
  margin: 20px 0;
  padding: 15px;
  border: 1px dashed #ccc;
  border-radius: 4px;
}

/* Responsive design */
@media (max-width: 768px) {
  .test-component {
    padding: 10px;
  }
  
  .form {
    max-width: 100%;
  }
  
  .modal {
    margin: 10px;
  }
}
</style>

<style>
/* Global styles */
body.loading {
  cursor: wait;
}

.focused {
  box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);
}
</style>
