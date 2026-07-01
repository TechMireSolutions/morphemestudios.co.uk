import Reveal from '../components/Reveal.jsx'

export default function Terms() {
  return (
    <div className="page">
      <header className="page-head wrap">
        <Reveal><p className="label">Legal</p></Reveal>
        <h1 className="display page-title">Terms of Use</h1>
      </header>
      <section className="section">
        <div className="wrap maxw-900 body-muted lead">
          <div className="contact-block">
            <p className="mt-s">Our website is for information purposes only. We don't collect cookies and don't store your personal data. However if you believe that your personal data has been incorrectly used, obtained or stored, please let us know by sending an e-mail to: <a href="mailto:connect@morphemestudios.com" className="link-u">connect@morphemestudios.com</a></p>
          </div>
          
          <div className="contact-block mt-l">
            <p className="label">Copyright</p>
            <p className="mt-s">Morpheme Studios is the owner and/or user of the copyright of all images displayed on this website. None of it can be used, copied, or multiplied without our written permission. Morpheme Studios cannot be held responsible for the information displayed or for the consequences of it being used by third parties.</p>
          </div>

          <div className="contact-block mt-l">
            <p className="mt-s">Our Terms of Use may change. If any changes occur, you will find the most recent update on this page.</p>
          </div>
        </div>
      </section>
    </div>
  )
}
