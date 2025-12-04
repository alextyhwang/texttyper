import matplotlib.pyplot as plt
import numpy as np
from engine.timing import TimingEngine

def test_keystroke_delays_with_bursts(wpm=60, num_chars=500):
    timing = TimingEngine(wpm=wpm, think_pause_min=2.0, think_pause_max=4.0)
    
    test_text = """The quick brown fox jumps over the lazy dog. This is a test sentence to measure typing speed. 
Human typing has natural variations and pauses between words. Sometimes we type faster, sometimes slower.
The rhythm of typing changes based on familiarity with words. Another sentence here. And one more to go.
Final thoughts come at the end. We should see burst patterns now. The pauses will be visible.""" * 3
    
    delays = []
    burst_markers = []
    prev_char = ''
    sentence_count = 0
    burst_threshold = 2
    next_burst_at = burst_threshold
    
    timing.start_new_burst()
    
    for i, char in enumerate(test_text[:num_chars]):
        delay = timing.get_keystroke_delay(prev_char, char)
        
        if prev_char == ' ':
            word_pause = timing.get_word_pause()
            delay += word_pause
        
        if char in '.!?':
            sentence_count += 1
            if sentence_count >= next_burst_at:
                think_pause = timing.get_think_pause()
                delays.append(delay + think_pause)
                burst_markers.append(i)
                timing.start_new_burst()
                next_burst_at = sentence_count + np.random.randint(2, 4)
            else:
                delays.append(delay)
        else:
            delays.append(delay)
        
        prev_char = char
    
    return delays, burst_markers

def test_gaussian_distribution(wpm=60, samples=1000):
    timing = TimingEngine(wpm=wpm)
    delays = []
    for _ in range(samples):
        timing.chars_typed = 0
        delay = timing.get_keystroke_delay('a', 'b')
        delays.append(delay)
    return delays

def plot_results():
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    delays_60, bursts_60 = test_keystroke_delays_with_bursts(wpm=60)
    delays_120, bursts_120 = test_keystroke_delays_with_bursts(wpm=120)
    delays_200, _ = test_keystroke_delays_with_bursts(wpm=200)
    
    ax1 = axes[0, 0]
    ax1.plot(delays_60, alpha=0.7, label='60 WPM', linewidth=0.8)
    ax1.plot(delays_120, alpha=0.7, label='120 WPM', linewidth=0.8)
    ax1.plot(delays_200, alpha=0.7, label='200 WPM', linewidth=0.8)
    for burst in bursts_60:
        ax1.axvline(x=burst, color='red', alpha=0.3, linestyle='--')
    ax1.set_xlabel('Character Index')
    ax1.set_ylabel('Delay (seconds)')
    ax1.set_title('Keystroke Delays with Burst Pauses (red lines)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    ax2 = axes[0, 1]
    delays_60_no_bursts = [d for d in delays_60 if d < 1.0]
    delays_120_no_bursts = [d for d in delays_120 if d < 1.0]
    ax2.hist(delays_60_no_bursts, bins=50, alpha=0.5, label='60 WPM', density=True)
    ax2.hist(delays_120_no_bursts, bins=50, alpha=0.5, label='120 WPM', density=True)
    ax2.set_xlabel('Delay (seconds)')
    ax2.set_ylabel('Density')
    ax2.set_title('Distribution of Keystroke Delays (excluding bursts)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    gaussian_delays = test_gaussian_distribution(wpm=60)
    ax3 = axes[1, 0]
    ax3.hist(gaussian_delays, bins=50, alpha=0.7, color='green', density=True)
    mean_delay = np.mean(gaussian_delays)
    std_delay = np.std(gaussian_delays)
    x = np.linspace(min(gaussian_delays), max(gaussian_delays), 100)
    gaussian_curve = (1/(std_delay * np.sqrt(2*np.pi))) * np.exp(-0.5*((x-mean_delay)/std_delay)**2)
    ax3.plot(x, gaussian_curve, 'r-', linewidth=2, label=f'Gaussian fit (μ={mean_delay:.3f}, σ={std_delay:.3f})')
    ax3.set_xlabel('Delay (seconds)')
    ax3.set_ylabel('Density')
    ax3.set_title('Gaussian Distribution Test (same char pair, 1000 samples)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    cumulative_60 = np.cumsum(delays_60)
    cumulative_120 = np.cumsum(delays_120)
    ax4 = axes[1, 1]
    ax4.plot(cumulative_60, label='60 WPM', linewidth=1.5)
    ax4.plot(cumulative_120, label='120 WPM', linewidth=1.5)
    for burst in bursts_60:
        ax4.axvline(x=burst, color='red', alpha=0.3, linestyle='--')
    ax4.set_xlabel('Characters Typed')
    ax4.set_ylabel('Total Time (seconds)')
    ax4.set_title('Cumulative Typing Time (red = burst pauses)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    total_time_60 = cumulative_60[-1]
    total_time_120 = cumulative_120[-1]
    typing_chars_60 = len(delays_60)
    typing_chars_120 = len(delays_120)
    
    actual_wpm_60 = typing_chars_60 / (total_time_60 / 60) / 5
    actual_wpm_120 = typing_chars_120 / (total_time_120 / 60) / 5
    
    plt.suptitle(f'Typing Timing Analysis (with bursts & pauses)\nActual WPM: 60→{actual_wpm_60:.1f}, 120→{actual_wpm_120:.1f}', fontsize=14)
    plt.tight_layout()
    plt.savefig('timing_analysis.png', dpi=150)
    plt.show()
    
    print(f"\n=== Timing Statistics ===")
    print(f"Target 60 WPM → Actual: {actual_wpm_60:.1f} WPM (including pauses)")
    print(f"Target 120 WPM → Actual: {actual_wpm_120:.1f} WPM (including pauses)")
    print(f"\n60 WPM delays: min={min(delays_60):.4f}s, max={max(delays_60):.4f}s, mean={np.mean(delays_60):.4f}s")
    print(f"120 WPM delays: min={min(delays_120):.4f}s, max={max(delays_120):.4f}s, mean={np.mean(delays_120):.4f}s")
    print(f"\nBurst pauses at 60 WPM: {len(bursts_60)} pauses")
    print(f"Gaussian σ = {std_delay:.4f} (wider = more variation)")

def test_burst_pattern():
    print("\n=== Testing Burst Pattern ===")
    from engine.typer import Typer
    
    typer = Typer(wpm=60, burst_min=2, burst_max=3, think_pause_min=2.0, think_pause_max=4.0)
    
    test_text = "First sentence here. Second sentence now. Third one coming. Fourth in line. Fifth appears. Sixth shows up. Seventh arrives. Eighth is here."
    
    typer._last_burst_count = 0
    typer._next_burst_at = 2
    
    print(f"Burst settings: {typer.burst_min}-{typer.burst_max} sentences")
    print(f"Think pause: {typer.timing.think_pause_min}-{typer.timing.think_pause_max}s")
    
    sentence_count = 0
    for i, char in enumerate(test_text):
        if char in '.!?':
            sentence_count += 1
            should_pause = typer._should_burst_pause(test_text[:i+1])
            if should_pause:
                pause = typer.timing.get_think_pause()
                print(f"  Sentence {sentence_count}: PAUSE for {pause:.2f}s")
            else:
                print(f"  Sentence {sentence_count}: continue typing")

if __name__ == "__main__":
    test_burst_pattern()
    print("\nGenerating plots...")
    plot_results()
