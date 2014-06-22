require 'formula'

class Libdwarf < Formula
  homepage 'http://libdwarf.sourceforge.net/'
  url 'git://git.code.sf.net/p/libdwarf/code', :tag => '20130729'

  depends_on 'libelf'

  def install
    chdir 'libdwarf' do
      system "./configure", "--disable-debug",
                            "--disable-dependency-tracking",
                            "--prefix=#{prefix}"
      system "make"
      lib.install 'libdwarf.a'
      include.install ['dwarf.h', 'libdwarf.h']
    end
  end
end
