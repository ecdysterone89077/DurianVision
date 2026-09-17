import { Link } from 'react-router-dom';

export default function ROISelector() {
  return (
    <div className="bg-background text-on-surface font-body-md h-screen w-full overflow-hidden flex flex-col antialiased">
      {/* TopNavBar */}
      <header className="bg-surface-dim text-primary flex justify-between items-center w-full px-lg py-sm relative z-50">
        <div className="font-headline-sm text-headline-sm font-bold text-primary flex items-center gap-sm">
          <span className="material-symbols-outlined" data-icon="precision_manufacturing">precision_manufacturing</span>
          DurianVision v1.0
        </div>
        <div className="hidden"></div>
        <div className="flex items-center gap-md">
          <button aria-label="Minimize" className="hover:bg-surface-variant transition-colors rounded p-xs text-on-surface-variant">
            <span className="material-symbols-outlined" data-icon="minimize">minimize</span>
          </button>
          <button aria-label="Maximize" className="hover:bg-surface-variant transition-colors rounded p-xs text-on-surface-variant">
            <span className="material-symbols-outlined" data-icon="maximize">maximize</span>
          </button>
          <Link to="/dashboard" aria-label="Close" className="hover:bg-error-container hover:text-on-error-container transition-colors rounded p-xs text-on-surface-variant block">
            <span className="material-symbols-outlined" data-icon="close">close</span>
          </Link>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="relative flex-grow w-full h-full bg-surface-container-lowest">
        <div 
          className="absolute inset-0 bg-cover bg-center z-0" 
          style={{ backgroundImage: "url('https://lh3.googleusercontent.com/aida-public/AB6AXuA6KTwfb3ZlUWvrFxDZDgY72GK_yte1Zj-l72cKxQHeFT6lRTjelwxmXjZBO1t_DqqhWHRiJOaDGbYI_ZuSQniER8RNndClv9AecZlG3TB6UOT6v0b4GPWMGeUF0n5kW7zpbd9ud9dW2iV7nPmjFgKxoXOXGOOjwI1Q1VlpGIy60BHn2H2UBMV2yBn81DXfvncmwc7z9RyvEwFbmMKfspKfOgMg97utUTNurwNctVmwLd1UN2MWrLcIYQ')" }}
        ></div>
        <div className="absolute inset-0 bg-grid-pattern z-0 opacity-50 pointer-events-none"></div>

        <div className="absolute inset-0 z-10 flex flex-col items-center justify-center no-select pointer-events-none">
          <div className="roi-box border-2 border-primary rounded w-[640px] h-[360px] relative pointer-events-auto flex items-center justify-center group cursor-move">
            <div className="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-primary -translate-x-0.5 -translate-y-0.5 cursor-nwse-resize"></div>
            <div className="absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 border-primary translate-x-0.5 -translate-y-0.5 cursor-nesw-resize"></div>
            <div className="absolute bottom-0 left-0 w-3 h-3 border-b-2 border-l-2 border-primary -translate-x-0.5 translate-y-0.5 cursor-nesw-resize"></div>
            <div className="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-primary translate-x-0.5 translate-y-0.5 cursor-nwse-resize"></div>
            
            <div className="bg-surface-container-high/80 text-primary font-mono-data text-mono-data px-sm py-xs rounded border border-outline-variant backdrop-blur-sm opacity-0 group-hover:opacity-100 transition-opacity">
              1280x720px
            </div>
          </div>

          <div className="mt-lg pointer-events-auto">
            <div className="bg-surface-container/90 border border-outline-variant rounded-lg p-md backdrop-blur-md shadow-[0_4px_24px_rgba(0,0,0,0.5)] flex flex-col gap-sm min-w-[320px]">
              <div className="flex items-center gap-sm border-b border-surface-container-highest pb-xs mb-xs">
                <span className="material-symbols-outlined text-tertiary" data-icon="tune">tune</span>
                <h3 className="font-label-caps text-label-caps text-on-surface tracking-wider">Region of Interest</h3>
              </div>
              <div className="grid grid-cols-1 gap-xs font-mono-data text-mono-data">
                <div className="flex justify-between items-center bg-surface-container-low p-xs rounded">
                  <span className="text-on-surface-variant flex items-center gap-xs">
                    <span className="material-symbols-outlined text-[16px]" data-icon="smartphone">smartphone</span> Device:
                  </span>
                  <span className="text-on-surface">Smartphone (9:16)</span>
                </div>
                <div className="flex justify-between items-center bg-surface-container-low p-xs rounded">
                  <span className="text-on-surface-variant flex items-center gap-xs">
                    <span className="material-symbols-outlined text-[16px]" data-icon="aspect_ratio">aspect_ratio</span> Resolution:
                  </span>
                  <span className="text-on-surface">390x844px</span>
                </div>
                <div className="flex justify-between items-center bg-surface-container-low p-xs rounded">
                  <span className="text-on-surface-variant flex items-center gap-xs">
                    <span className="material-symbols-outlined text-[16px]" data-icon="speed">speed</span> Auto FPS:
                  </span>
                  <span className="text-primary font-bold">5</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="absolute bottom-xl left-1/2 -translate-x-1/2 z-20 flex gap-md bg-surface-container-high/90 p-xs rounded-full backdrop-blur-md border border-outline-variant">
          <Link to="/dashboard" className="px-lg py-sm rounded-full font-label-caps text-label-caps bg-surface-container-low text-on-surface hover:bg-surface-variant hover:text-primary transition-colors flex items-center gap-xs">
            <span className="material-symbols-outlined text-[18px]" data-icon="close">close</span>
            Cancel
          </Link>
          <button className="px-lg py-sm rounded-full font-label-caps text-label-caps bg-surface-container-low text-on-surface hover:bg-surface-variant hover:text-primary transition-colors flex items-center gap-xs">
            <span className="material-symbols-outlined text-[18px]" data-icon="fullscreen">fullscreen</span>
            Full Screen
          </button>
          <Link to="/dashboard" className="px-lg py-sm rounded-full font-label-caps text-label-caps bg-primary text-on-primary hover:bg-primary-fixed transition-colors flex items-center gap-xs shadow-[0_0_12px_rgba(75,226,119,0.3)]">
            <span className="material-symbols-outlined text-[18px]" data-icon="check">check</span>
            Confirm
          </Link>
        </div>
      </main>

      <footer className="bg-surface-container-highest text-tertiary font-mono-data text-mono-data fixed bottom-0 left-0 w-full z-50 flex justify-between items-center px-lg py-xs border-t-0">
        <div className="flex items-center gap-sm">
          <span className="w-2 h-2 rounded-full bg-primary animate-pulse shadow-[0_0_8px_rgba(75,226,119,0.8)]"></span>
          Detection Active | 60 FPS | NVIDIA RTX 4090 | Area: <span className="text-primary">Optimal</span>
        </div>
        <div className="flex gap-md">
          <a className="text-on-surface-variant hover:text-primary transition-colors" href="#">System Logs</a>
          <a className="text-on-surface-variant hover:text-primary transition-colors" href="#">Network Status</a>
          <a className="text-on-surface-variant hover:text-primary transition-colors" href="#">API v2.1</a>
        </div>
      </footer>
    </div>
  );
}
