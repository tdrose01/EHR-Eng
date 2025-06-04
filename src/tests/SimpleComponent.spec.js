import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { defineComponent } from 'vue'

// Create a simple counter component for testing
const CounterComponent = defineComponent({
  template: `
    <div>
      <span class="count">{{ count }}</span>
      <button class="increment" @click="increment">Increment</button>
    </div>
  `,
  data() {
    return {
      count: 0
    }
  },
  methods: {
    increment() {
      this.count++
    }
  }
})

describe('Counter Component', () => {
  it('renders with initial count of 0', () => {
    const wrapper = mount(CounterComponent)
    expect(wrapper.find('.count').text()).toBe('0')
  })

  it('increments count when button is clicked', async () => {
    const wrapper = mount(CounterComponent)
    await wrapper.find('.increment').trigger('click')
    expect(wrapper.find('.count').text()).toBe('1')
  })
}) 